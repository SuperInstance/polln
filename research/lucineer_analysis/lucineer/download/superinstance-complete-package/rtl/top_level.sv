/**
 * TernaryAir RTL Package
 * Top-Level Inference Engine
 * 
 * MIT License - Open Source Hardware
 * Author: Casey DiGennaro
 * Repository: github.com/superinstance/ternaryair
 * 
 * This is the top-level module integrating all components:
 *   - Synaptic Array (RAU-based compute)
 *   - Weight ROM (non-ternary parameters)
 *   - KV Cache (attention state)
 *   - Controller (operation sequencing)
 *   - I/O Interface (USB/PCIe communication)
 */

module ternaryair_top #(
    // Model parameters
    parameter int NUM_LAYERS = 24,
    parameter int HIDDEN_SIZE = 2048,
    parameter int INTERMEDIATE_SIZE = 8192,
    parameter int NUM_HEADS = 16,
    parameter int HEAD_DIM = HIDDEN_SIZE / NUM_HEADS,
    parameter int MAX_SEQ_LEN = 4096,
    
    // Hardware parameters
    parameter int ARRAY_ROWS = 256,
    parameter int ARRAY_COLS = 256,
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24,
    
    // I/O parameters
    parameter int USB_PACKET_SIZE = 64
)(
    input  logic                        clk,
    input  logic                        rst_n,
    
    // USB/PCIe Interface
    input  logic [7:0]                  usb_data_in,
    input  logic                        usb_data_valid,
    output logic [7:0]                  usb_data_out,
    output logic                        usb_data_ready,
    
    // Power management
    output logic [2:0]                  power_state,  // 0=active, 1=idle, 2=sleep, 3=deep_sleep
    output logic [15:0]                 temperature,   // In 0.1°C units
    output logic [15:0]                 power_consumption_mw
);

    // ============= Internal Signals =============
    
    // Controller state
    logic [3:0] controller_state;
    logic [7:0] layer_counter;
    logic [$clog2(MAX_SEQ_LEN):0] token_counter;
    logic [31:0] operation_counter;
    
    // Synaptic array interface
    logic [ACTIVATION_WIDTH-1:0] array_activations [ARRAY_COLS];
    logic array_activation_valid;
    logic [1:0] array_weights [ARRAY_ROWS][ARRAY_COLS];
    logic array_compute_en;
    logic [ACCUMULATOR_WIDTH-1:0] array_results [ARRAY_ROWS];
    logic array_results_valid;
    
    // Weight ROM interface
    logic [$clog2(HIDDEN_SIZE)-1:0] weight_addr;
    logic [15:0] weight_data;
    logic weight_valid;
    
    // KV Cache interface
    logic kv_write_en;
    logic kv_read_en;
    logic [$clog2(NUM_LAYERS)-1:0] kv_layer;
    logic kv_is_value;
    logic [$clog2(NUM_HEADS)-1:0] kv_head;
    logic [$clog2(MAX_SEQ_LEN)-1:0] kv_pos;
    logic [3:0] kv_write_data;
    logic [3:0] kv_read_data;
    logic kv_read_valid;
    
    // Activation buffers
    logic [ACTIVATION_WIDTH-1:0] input_buffer [HIDDEN_SIZE];
    logic [ACTIVATION_WIDTH-1:0] hidden_buffer [HIDDEN_SIZE];
    logic [ACTIVATION_WIDTH-1:0] output_buffer [HIDDEN_SIZE];
    
    // Control signals
    logic compute_start;
    logic compute_done;
    logic layer_done;
    logic inference_done;

    // ============= Controller State Machine =============
    
    localparam STATE_IDLE      = 4'd0;
    localparam STATE_RECEIVE   = 4'd1;
    localparam STATE_EMBED     = 4'd2;
    localparam STATE_ATTN_Q    = 4'd3;
    localparam STATE_ATTN_KV   = 4'd4;
    localparam STATE_ATTN_OUT  = 4'd5;
    localparam STATE_FFN_UP    = 4'd6;
    localparam STATE_FFN_ACT   = 4'd7;
    localparam STATE_FFN_DOWN  = 4'd8;
    localparam STATE_OUTPUT    = 4'd9;
    localparam STATE_SEND      = 4'd10;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            controller_state <= STATE_IDLE;
            layer_counter <= '0;
            token_counter <= '0;
            operation_counter <= '0;
            compute_start <= 1'b0;
        end else begin
            case (controller_state)
                STATE_IDLE: begin
                    if (usb_data_valid && usb_data_in == 8'hAA) begin // Start token
                        controller_state <= STATE_RECEIVE;
                        token_counter <= '0;
                    end
                    compute_start <= 1'b0;
                end
                
                STATE_RECEIVE: begin
                    // Receive input tokens
                    if (usb_data_valid) begin
                        input_buffer[token_counter[$clog2(HIDDEN_SIZE)-1:0]] <= {usb_data_in, usb_data_in};
                        token_counter <= token_counter + 1;
                        if (token_counter >= HIDDEN_SIZE - 1) begin
                            controller_state <= STATE_EMBED;
                            layer_counter <= '0;
                        end
                    end
                end
                
                STATE_EMBED: begin
                    // Token embedding (lookup table - simplified)
                    controller_state <= STATE_ATTN_Q;
                end
                
                STATE_ATTN_Q: begin
                    // Compute Q projection
                    compute_start <= 1'b1;
                    if (compute_done) begin
                        controller_state <= STATE_ATTN_KV;
                        compute_start <= 1'b0;
                    end
                end
                
                STATE_ATTN_KV: begin
                    // Compute K,V projections and attention
                    if (compute_done) begin
                        controller_state <= STATE_ATTN_OUT;
                    end
                end
                
                STATE_ATTN_OUT: begin
                    // Output projection
                    if (compute_done) begin
                        if (layer_counter < NUM_LAYERS - 1) begin
                            layer_counter <= layer_counter + 1;
                            controller_state <= STATE_ATTN_Q;
                        end else begin
                            controller_state <= STATE_FFN_UP;
                        end
                    end
                end
                
                STATE_FFN_UP: begin
                    // FFN up projection (HIDDEN -> INTERMEDIATE)
                    layer_counter <= '0;
                    if (compute_done) begin
                        controller_state <= STATE_FFN_ACT;
                    end
                end
                
                STATE_FFN_ACT: begin
                    // Activation function (GELU approximation)
                    controller_state <= STATE_FFN_DOWN;
                end
                
                STATE_FFN_DOWN: begin
                    // FFN down projection (INTERMEDIATE -> HIDDEN)
                    if (compute_done) begin
                        if (layer_counter < NUM_LAYERS - 1) begin
                            layer_counter <= layer_counter + 1;
                            controller_state <= STATE_ATTN_Q;
                        end else begin
                            controller_state <= STATE_OUTPUT;
                        end
                    end
                end
                
                STATE_OUTPUT: begin
                    // LM head (project to vocabulary)
                    controller_state <= STATE_SEND;
                end
                
                STATE_SEND: begin
                    // Transmit output token
                    if (usb_data_ready) begin
                        // Send complete
                        controller_state <= STATE_IDLE;
                    end
                end
                
                default: controller_state <= STATE_IDLE;
            endcase
            
            operation_counter <= operation_counter + 1;
        end
    end
    
    assign compute_done = array_results_valid;

    // ============= Synaptic Array Instance =============
    
    synaptic_array #(
        .NUM_ROWS(ARRAY_ROWS),
        .NUM_COLS(ARRAY_COLS),
        .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
        .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH)
    ) synaptic_array_inst (
        .clk(clk),
        .rst_n(rst_n),
        .activations(array_activations),
        .activation_valid(array_activation_valid),
        .weights(array_weights),
        .compute_en(array_compute_en),
        .row_rst('{default: 1'b0}),
        .results(array_results),
        .results_valid(array_results_valid)
    );
    
    // ============= Weight ROM Instance =============
    
    weight_rom #(
        .DEPTH(HIDDEN_SIZE * 4),  // LayerNorm gamma, beta, etc.
        .DATA_WIDTH(16)
    ) weight_rom_inst (
        .clk(clk),
        .addr(weight_addr),
        .data(weight_data)
    );
    
    // ============= KV Cache Instance =============
    
    kv_cache #(
        .NUM_LAYERS(NUM_LAYERS),
        .NUM_HEADS(NUM_HEADS),
        .HEAD_DIM(HEAD_DIM),
        .MAX_SEQ_LEN(MAX_SEQ_LEN)
    ) kv_cache_inst (
        .clk(clk),
        .rst_n(rst_n),
        .write_en(kv_write_en),
        .write_layer(kv_layer),
        .write_is_value(kv_is_value),
        .write_head(kv_head),
        .write_pos(kv_pos),
        .write_data(kv_write_data),
        .read_en(kv_read_en),
        .read_layer(kv_layer),
        .read_is_value(kv_is_value),
        .read_head(kv_head),
        .read_pos(kv_pos),
        .read_data(kv_read_data),
        .read_valid(kv_read_valid),
        .current_seq_len(token_counter),
        .cache_full(),
        .cache_clear(1'b0)
    );
    
    // ============= Power Management =============
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            power_state <= 3'b010;  // Idle
        end else begin
            case (controller_state)
                STATE_IDLE: power_state <= 3'b010;     // Idle
                STATE_RECEIVE: power_state <= 3'b000;  // Active
                STATE_EMBED, STATE_ATTN_Q, STATE_ATTN_KV,
                STATE_ATTN_OUT, STATE_FFN_UP, STATE_FFN_DOWN: 
                    power_state <= 3'b000;              // Active
                STATE_SEND: power_state <= 3'b000;     // Active
                default: power_state <= 3'b010;        // Idle
            endcase
        end
    end
    
    // Power estimation (simplified model)
    assign power_consumption_mw = (power_state == 3'b000) ? 3500 : 
                                  (power_state == 3'b010) ? 50 : 10;
    
    // Temperature sensor interface (placeholder)
    assign temperature = 16'd250;  // 25.0°C default

    // ============= USB Output Interface =============
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            usb_data_out <= '0;
            usb_data_ready <= 1'b0;
        end else if (controller_state == STATE_SEND) begin
            usb_data_out <= output_buffer[0][7:0];  // Simplified
            usb_data_ready <= 1'b1;
        end else begin
            usb_data_ready <= 1'b0;
        end
    end

endmodule
