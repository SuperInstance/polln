//-----------------------------------------------------------------------------
// Module: top_level
// Description: Main inference engine for TernaryAir
//
// TernaryAir - Open Source Air-Gapped Inference Hardware
// Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)
// MIT License - https://opensource.org/licenses/MIT
//
// This is the top-level module that instantiates and connects all
// sub-components of the TernaryAir inference engine.
//
// Architecture:
//   USB → Protocol Handler → Input Buffer → PE Array → KV Cache → Output
//                                   ↑              ↑
//                              Weight ROM (mask-locked)
//
// Author: Casey DiGennaro
// Version: 1.0
//-----------------------------------------------------------------------------

module top_level #(
    // Data widths
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24,
    
    // Array dimensions
    parameter int NUM_COLUMNS = 12,
    parameter int NUM_ROWS = 8,
    
    // Model parameters
    parameter int HIDDEN_DIM = 1024,
    parameter int NUM_LAYERS = 24,
    parameter int VOCAB_SIZE = 32000,
    
    // Memory sizes
    parameter int EMBEDDING_SIZE = VOCAB_SIZE * ACTIVATION_WIDTH,
    parameter int KV_CACHE_SIZE = 512 * 1024  // 512KB
)(
    // Clock and reset
    input  logic        clk,
    input  logic        rst_n,
    
    // USB Interface (simplified for RTL)
    input  logic        usb_rx_valid,
    input  logic [7:0]  usb_rx_data,
    output logic        usb_tx_valid,
    output  logic [7:0]  usb_tx_data,
    output logic        usb_tx_ready,
    
    // Status outputs
    output logic [7:0]  status,
    output logic [11:0] temperature,
    output logic        thermal_warning,
    
    // Debug interface
    input  logic        debug_enable,
    input  logic [3:0]  debug_select,
    output logic [31:0] debug_data
);

    //=========================================================================
    // Local parameters and types
    //=========================================================================
    
    // Status register bits
    localparam bit [7:0] STATUS_IDLE      = 8'h00;
    localparam bit [7:0] STATUS_RECEIVING = 8'h01;
    localparam bit [7:0] STATUS_INFERRING = 8'h02;
    localparam bit [7:0] STATUS_SENDING   = 8'h03;
    localparam bit [7:0] STATUS_ERROR     = 8'hFF;
    
    // State machine states
    typedef enum logic [3:0] {
        IDLE,
        RECEIVE_INPUT,
        TOKENIZE,
        EMBED_LOOKUP,
        LAYER_LOOP,
        ATTENTION,
        MLP,
        OUTPUT_LAYER,
        DETOKENIZE,
        TRANSMIT,
        ERROR_STATE
    } state_t;
    
    //=========================================================================
    // Internal signals
    //=========================================================================
    
    // State machine
    state_t current_state, next_state;
    
    // Control signals
    logic        start_inference;
    logic        inference_done;
    logic [5:0]  layer_counter;
    logic        layer_done;
    logic        attention_done;
    logic        mlp_done;
    
    // Token interface
    logic [15:0] input_token;
    logic [15:0] output_token;
    logic        token_valid;
    
    // Activation bus (between modules)
    logic signed [ACTIVATION_WIDTH-1:0] activation_in   [NUM_COLUMNS];
    logic signed [ACTIVATION_WIDTH-1:0] activation_out  [NUM_COLUMNS];
    
    // Weight bus
    logic [1:0] weight_bus [NUM_COLUMNS][NUM_ROWS];
    
    // Partial sums from PE array
    logic signed [ACCUMULATOR_WIDTH-1:0] partial_sums [NUM_COLUMNS];
    
    // KV Cache interface
    logic        kv_write_enable;
    logic        kv_read_enable;
    logic [17:0] kv_address;  // 512KB = 2^18 bytes
    logic [63:0] kv_write_data;
    logic [63:0] kv_read_data;
    
    // Input/Output buffers
    logic [7:0]  input_buffer  [0:4095];  // 4KB input buffer
    logic [15:0] input_buffer_write_ptr;
    logic [15:0] input_buffer_read_ptr;
    
    logic [7:0]  output_buffer [0:4095];  // 4KB output buffer
    logic [15:0] output_buffer_write_ptr;
    logic [15:0] output_buffer_read_ptr;
    
    // Embedding interface
    logic signed [ACTIVATION_WIDTH-1:0] embedding_vector [HIDDEN_DIM-1:0];
    logic        embedding_valid;
    
    //=========================================================================
    // Module instantiations
    //=========================================================================
    
    // Synaptic array (PE array with RAUs)
    synaptic_array #(
        .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
        .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH),
        .NUM_COLUMNS(NUM_COLUMNS),
        .NUM_ROWS(NUM_ROWS)
    ) u_synaptic_array (
        .clk(clk),
        .rst_n(rst_n),
        
        // Activations
        .activations_in(activation_in),
        .activations_out(activation_out),
        
        // Weights from ROM
        .weights(weight_bus),
        
        // Results
        .partial_sums(partial_sums),
        
        // Control
        .compute_enable(current_state == LAYER_LOOP || 
                        current_state == MLP ||
                        current_state == ATTENTION),
        .clear_accumulator(current_state == IDLE)
    );
    
    // Weight ROM (mask-locked)
    weight_rom #(
        .NUM_LAYERS(NUM_LAYERS),
        .HIDDEN_DIM(HIDDEN_DIM),
        .NUM_COLUMNS(NUM_COLUMNS),
        .NUM_ROWS(NUM_ROWS)
    ) u_weight_rom (
        .clk(clk),
        .rst_n(rst_n),
        
        // Layer/column selection
        .layer_select(layer_counter),
        .column_select(/* determined by state machine */),
        
        // Weight output
        .weights(weight_bus),
        
        // Control
        .rom_enable(current_state == LAYER_LOOP || 
                    current_state == MLP ||
                    current_state == ATTENTION)
    );
    
    // KV Cache
    kv_cache #(
        .CACHE_SIZE(KV_CACHE_SIZE)
    ) u_kv_cache (
        .clk(clk),
        .rst_n(rst_n),
        
        // Memory interface
        .write_enable(kv_write_enable),
        .read_enable(kv_read_enable),
        .address(kv_address),
        .write_data(kv_write_data),
        .read_data(kv_read_data),
        
        // Control
        .cache_clear(current_state == IDLE && start_inference)
    );
    
    //=========================================================================
    // State machine
    //=========================================================================
    
    // State transition
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
        end else begin
            current_state <= next_state;
        end
    end
    
    // Next state logic
    always_comb begin
        next_state = current_state;  // Default: stay in current state
        
        case (current_state)
            IDLE: begin
                if (start_inference)
                    next_state = RECEIVE_INPUT;
            end
            
            RECEIVE_INPUT: begin
                if (input_buffer_write_ptr == 0)  // Done receiving
                    next_state = TOKENIZE;
            end
            
            TOKENIZE: begin
                next_state = EMBED_LOOKUP;
            end
            
            EMBED_LOOKUP: begin
                if (embedding_valid)
                    next_state = LAYER_LOOP;
            end
            
            LAYER_LOOP: begin
                if (attention_done)
                    next_state = MLP;
                else if (layer_counter == NUM_LAYERS - 1)
                    next_state = OUTPUT_LAYER;
            end
            
            ATTENTION: begin
                if (attention_done)
                    next_state = LAYER_LOOP;
            end
            
            MLP: begin
                if (mlp_done) begin
                    if (layer_counter < NUM_LAYERS - 1)
                        next_state = LAYER_LOOP;
                    else
                        next_state = OUTPUT_LAYER;
                end
            end
            
            OUTPUT_LAYER: begin
                if (token_valid)
                    next_state = DETOKENIZE;
            end
            
            DETOKENIZE: begin
                next_state = TRANSMIT;
            end
            
            TRANSMIT: begin
                if (/* all output sent */ 1'b1)
                    next_state = IDLE;
            end
            
            ERROR_STATE: begin
                next_state = IDLE;
            end
            
            default: begin
                next_state = IDLE;
            end
        endcase
    end
    
    //=========================================================================
    // Layer counter
    //=========================================================================
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            layer_counter <= '0;
        end else if (current_state == IDLE) begin
            layer_counter <= '0;
        end else if (current_state == MLP && mlp_done) begin
            layer_counter <= layer_counter + 1'b1;
        end
    end
    
    //=========================================================================
    // Status output
    //=========================================================================
    
    always_comb begin
        case (current_state)
            IDLE:           status = STATUS_IDLE;
            RECEIVE_INPUT:  status = STATUS_RECEIVING;
            LAYER_LOOP,
            ATTENTION,
            MLP:            status = STATUS_INFERRING;
            TRANSMIT:       status = STATUS_SENDING;
            ERROR_STATE:    status = STATUS_ERROR;
            default:        status = STATUS_IDLE;
        endcase
    end
    
    //=========================================================================
    // Temperature sensor (simplified - would be analog in real chip)
    //=========================================================================
    
    // Simulated temperature based on activity
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            temperature <= 12'h120;  // ~18°C baseline
        end else if (current_state == LAYER_LOOP || 
                     current_state == ATTENTION ||
                     current_state == MLP) begin
            // Temperature rises during inference
            if (temperature < 12'h400)  // Max ~60°C
                temperature <= temperature + 1;
        end else begin
            // Cool down when idle
            if (temperature > 12'h120)
                temperature <= temperature - 1;
        end
    end
    
    assign thermal_warning = (temperature > 12'h380);  // Warning at ~56°C
    
    //=========================================================================
    // Debug interface
    //=========================================================================
    
    always_comb begin
        if (debug_enable) begin
            case (debug_select)
                4'h0: debug_data = {16'h0, status, temperature};
                4'h1: debug_data = {26'h0, layer_counter};
                4'h2: debug_data = partial_sums[0];
                4'h3: debug_data = partial_sums[1];
                default: debug_data = 32'h0;
            endcase
        end else begin
            debug_data = 32'h0;
        end
    end
    
    //=========================================================================
    // Formal verification assertions
    //=========================================================================
    
    `ifdef FORMAL
        // Always returns to IDLE eventually
        always @(posedge clk) begin
            if (current_state != IDLE) begin
                // Should return to IDLE within reasonable cycles
                assert(layer_counter < NUM_LAYERS + 5);
            end
        end
        
        // Temperature stays in bounds
        always @(posedge clk) begin
            assert(temperature < 12'h800);  // Max 128°C (impossible)
        end
    `endif

endmodule
