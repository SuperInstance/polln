//-----------------------------------------------------------------------------
// Module: superinstance_inference_engine
// Description: Top-level mask-locked inference engine for LLM edge inference
//
// Target Performance:
//   - Throughput: 80-150 tok/s
//   - Power: 2-5W
//   - Area: 42mm² @ 28nm
//
// Architecture:
//   - 20 Synaptic Array Tiles
//   - 1.31M ternary weights per layer pass
//   - Mask-locked weight ROM
//   - Hierarchical KV cache
//
// Author: SuperInstance.AI VP Manufacturing
// Version: 1.0
//-----------------------------------------------------------------------------

module superinstance_inference_engine #(
    // Model configuration
    parameter int NUM_LAYERS = 24,
    parameter int HIDDEN_DIM = 1024,
    parameter int NUM_HEADS = 16,
    parameter int HEAD_DIM = 64,
    parameter int MAX_SEQ_LEN = 4096,
    
    // Hardware configuration  
    parameter int NUM_TILES = 20,
    parameter int RAUS_PER_TILE = 256,
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24,
    
    // Derived parameters
    parameter int WEIGHTS_PER_LAYER = HIDDEN_DIM * HIDDEN_DIM * 3,  // QKV projection
    parameter int KV_CACHE_SIZE = MAX_SEQ_LEN * NUM_LAYERS * 2 * NUM_HEADS * HEAD_DIM
)(
    input  logic        clk,
    input  logic        rst_n,
    
    // Memory interface (for activations and KV cache)
    input  logic        mem_clk,
    input  logic [31:0] mem_addr,
    input  logic        mem_wr_en,
    input  logic        mem_rd_en,
    input  logic [63:0] mem_wr_data,
    output logic [63:0] mem_rd_data,
    output logic        mem_ack,
    
    // Control interface
    input  logic        start_inference,
    input  logic [15:0] sequence_length,
    input  logic [15:0] current_position,
    output logic        inference_done,
    output logic        token_valid,
    output logic [15:0] output_token,
    
    // Debug/Status
    output logic [31:0] cycle_counter,
    output logic [31:0] tokens_generated,
    output logic        busy,
    output logic        error
);

    //--------------------------------------------------------------------------
    // State machine definitions
    //--------------------------------------------------------------------------
    
    typedef enum logic [3:0] {
        IDLE            = 4'b0000,
        LOAD_ACTIVATION = 4'b0001,
        COMPUTE_QKV     = 4'b0010,
        COMPUTE_ATTN    = 4'b0011,
        UPDATE_KV       = 4'b0100,
        COMPUTE_MLP     = 4'b0101,
        OUTPUT_TOKEN    = 4'b0110,
        ERROR_STATE     = 4'b1111
    } state_t;

    //--------------------------------------------------------------------------
    // Internal signals
    //--------------------------------------------------------------------------
    
    state_t current_state, next_state;
    
    // Layer counter
    logic [4:0] layer_counter;
    logic layer_done;
    
    // Tile control
    logic [NUM_TILES-1:0] tile_en;
    logic [NUM_TILES-1:0] tile_busy;
    logic [NUM_TILES-1:0] tile_done;
    
    // Activation buffer (input to tiles)
    logic [NUM_TILES-1:0][RAUS_PER_TILE-1:0][ACTIVATION_WIDTH-1:0] tile_activations;
    logic activations_valid;
    
    // Weight ROM interface (mask-locked)
    logic [NUM_TILES-1:0][RAUS_PER_TILE-1:0][1:0] tile_weights;
    
    // Accumulator outputs
    logic signed [NUM_TILES-1:0][ACCUMULATOR_WIDTH-1:0] tile_results;
    logic [NUM_TILES-1:0] tile_result_valid;
    
    // Attention signals
    logic attention_phase;
    logic [NUM_HEADS-1:0] head_valid;
    
    //--------------------------------------------------------------------------
    // Weight ROM (Mask-Locked)
    // This would be generated from trained model weights
    // In actual silicon, this is hard-coded in metal patterns
    //--------------------------------------------------------------------------
    
    // Weight ROM for BitNet 2B model
    // In production: Generated from pytorch model via scripts/generate_weight_rom.py
    // For simulation: Initialize with test patterns
    
    // Weight bank selection (which layer/operation)
    logic [7:0] weight_bank_addr;
    
    mask_locked_weight_rom #(
        .NUM_TILES(NUM_TILES),
        .RAUS_PER_TILE(RAUS_PER_TILE),
        .NUM_LAYERS(NUM_LAYERS),
        .WEIGHT_BANKS(NUM_LAYERS * 4)  // 4 weight banks per layer: Q, K, V, MLP
    ) u_weight_rom (
        .clk(clk),
        .bank_select(weight_bank_addr),
        .weights_out(tile_weights)
    );

    //--------------------------------------------------------------------------
    // Synaptic Array Tiles
    //--------------------------------------------------------------------------
    
    generate
        for (genvar t = 0; t < NUM_TILES; t++) begin : gen_tiles
            synaptic_array #(
                .NUM_RAUS(RAUS_PER_TILE),
                .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
                .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH)
            ) u_tile (
                .clk(clk),
                .rst_n(rst_n),
                .activations(tile_activations[t]),
                .activations_valid(activations_valid && tile_en[t]),
                .weights(tile_weights[t]),
                .accumulate_en(1'b1),
                .clear_acc(current_state == LOAD_ACTIVATION),
                .partial_sum(tile_results[t]),
                .result_valid(tile_result_valid[t])
            );
        end
    endgenerate

    //--------------------------------------------------------------------------
    // KV Cache Management
    //--------------------------------------------------------------------------
    
    kv_cache_controller #(
        .NUM_LAYERS(NUM_LAYERS),
        .NUM_HEADS(NUM_HEADS),
        .HEAD_DIM(HEAD_DIM),
        .MAX_SEQ_LEN(MAX_SEQ_LEN),
        .ACTIVATION_WIDTH(ACTIVATION_WIDTH)
    ) u_kv_cache (
        .clk(mem_clk),
        .rst_n(rst_n),
        
        // KV update interface
        .kv_write_en(current_state == UPDATE_KV),
        .layer_select(layer_counter),
        .head_select(/* from attention */),
        .position(current_position),
        .kv_data_in(/* from QKV computation */),
        
        // KV read interface  
        .kv_read_en(current_state == COMPUTE_ATTN),
        .kv_data_out(/* to attention */),
        
        .cache_full(/* overflow indicator */)
    );

    //--------------------------------------------------------------------------
    // State Machine
    //--------------------------------------------------------------------------
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
            layer_counter <= '0;
            cycle_counter <= '0;
            tokens_generated <= '0;
        end else begin
            cycle_counter <= cycle_counter + 1;
            current_state <= next_state;
            
            case (current_state)
                COMPUTE_QKV: begin
                    if (layer_done) begin
                        layer_counter <= layer_counter + 1;
                    end
                end
                
                OUTPUT_TOKEN: begin
                    tokens_generated <= tokens_generated + 1;
                end
                
                default: ;
            endcase
        end
    end
    
    // State transitions
    always_comb begin
        next_state = current_state;
        
        case (current_state)
            IDLE: begin
                if (start_inference)
                    next_state = LOAD_ACTIVATION;
            end
            
            LOAD_ACTIVATION: begin
                next_state = COMPUTE_QKV;
            end
            
            COMPUTE_QKV: begin
                if (layer_counter == NUM_LAYERS - 1)
                    next_state = COMPUTE_ATTN;
                else if (layer_done)
                    next_state = COMPUTE_QKV;  // Continue with next layer
            end
            
            COMPUTE_ATTN: begin
                if (/* attention complete */ 1'b0)
                    next_state = UPDATE_KV;
            end
            
            UPDATE_KV: begin
                next_state = COMPUTE_MLP;
            end
            
            COMPUTE_MLP: begin
                if (/* MLP complete */ 1'b0)
                    next_state = OUTPUT_TOKEN;
            end
            
            OUTPUT_TOKEN: begin
                next_state = IDLE;
            end
            
            default: next_state = IDLE;
        endcase
    end

    //--------------------------------------------------------------------------
    // Status outputs
    //--------------------------------------------------------------------------
    
    assign busy = (current_state != IDLE);
    assign inference_done = (current_state == OUTPUT_TOKEN);

    //--------------------------------------------------------------------------
    // Performance monitoring (simulation only)
    //--------------------------------------------------------------------------
    
    `ifdef SIMULATION
        int tokens_per_second_counter;
        int last_second_cycle;
        
        always_ff @(posedge clk) begin
            if (cycle_counter - last_second_cycle >= 100_000_000) begin  // Assuming 100MHz
                $display("[%0t] Tokens/second: %0d", $time, tokens_per_second_counter);
                tokens_per_second_counter <= 0;
                last_second_cycle <= cycle_counter;
            end else if (token_valid) begin
                tokens_per_second_counter <= tokens_per_second_counter + 1;
            end
        end
    `endif

endmodule
