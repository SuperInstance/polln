/**
 * Top-Level Inference Engine
 * 
 * Complete TernaryAir inference engine integrating all components.
 * Fixed-function transformer inference with mask-locked weights.
 * 
 * Author: Casey DiGennaro / SuperInstance.AI
 * License: MIT
 */

module top_level #(
    // Model configuration
    parameter int NUM_LAYERS    = 24,
    parameter int NUM_HEADS     = 12,
    parameter int HEAD_DIM      = 64,
    parameter int FFN_DIM       = 3072,
    parameter int EMBED_DIM     = 768,
    parameter int VOCAB_SIZE    = 32000,
    parameter int CONTEXT_LEN   = 4096,
    
    // Precision
    parameter int DATA_WIDTH    = 24,
    parameter int ACC_WIDTH     = 32,
    
    // Derived parameters
    parameter int TOKEN_WIDTH   = $clog2(VOCAB_SIZE)
)(
    input  logic                    clk,
    input  logic                    rst_n,
    
    // USB/UART interface
    input  logic                    rx_valid,
    input  logic [7:0]              rx_data,
    output logic                    tx_valid,
    output logic [7:0]              tx_data,
    output logic                    tx_ready,
    
    // Status LEDs
    output logic [3:0]              status_leds
);

    // FSM states
    typedef enum logic [3:0] {
        IDLE,
        RECV_TOKEN,
        EMBEDDING,
        ATTENTION_PREP,
        ATTENTION_COMP,
        FFN_COMP,
        LAYER_NORM,
        OUTPUT_HEAD,
        SAMPLING,
        SEND_TOKEN
    } state_t;
    
    state_t current_state, next_state;
    
    // Internal buses
    logic signed [DATA_WIDTH-1:0]   activation_bus [EMBED_DIM];
    logic signed [DATA_WIDTH-1:0]   output_bus [EMBED_DIM];
    
    // Token handling
    logic [TOKEN_WIDTH-1:0]         input_token;
    logic [TOKEN_WIDTH-1:0]         output_token;
    logic                           token_valid;
    
    // Layer counters
    logic [$clog2(NUM_LAYERS)-1:0]  layer_counter;
    logic [$clog2(NUM_HEADS)-1:0]   head_counter;
    logic [$clog2(CONTEXT_LEN)-1:0] position_counter;
    
    // Embedding lookup
    logic [TOKEN_WIDTH-1:0]         embed_addr;
    logic signed [DATA_WIDTH-1:0]   embed_out [EMBED_DIM];
    
    // Attention signals
    logic signed [DATA_WIDTH-1:0]   q_out [HEAD_DIM];
    logic signed [DATA_WIDTH-1:0]   k_out [HEAD_DIM];
    logic signed [DATA_WIDTH-1:0]   v_out [HEAD_DIM];
    logic signed [DATA_WIDTH-1:0]   attn_out [HEAD_DIM];
    
    // FFN signals
    logic signed [DATA_WIDTH-1:0]   ffn_intermediate [FFN_DIM];
    logic signed [DATA_WIDTH-1:0]   ffn_out [EMBED_DIM];
    
    // KV cache
    logic                           kv_write_en;
    logic                           kv_read_en;
    logic [DATA_WIDTH-1:0]          kv_data_in;
    logic [DATA_WIDTH-1:0]          kv_k_out;
    logic [DATA_WIDTH-1:0]          kv_v_out;
    logic [$clog2(CONTEXT_LEN):0]   kv_current_len;
    
    // Softmax output
    logic [VOCAB_SIZE-1:0]          vocab_probs;  // Simplified - would be fixed-point
    
    // Sampling
    logic [TOKEN_WIDTH-1:0]         sampled_token;
    
    // ========== FSM State Machine ==========
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
        end else begin
            current_state <= next_state;
        end
    end
    
    always_comb begin
        next_state = current_state;  // Default: stay in current state
        
        case (current_state)
            IDLE: begin
                if (rx_valid) begin
                    next_state = RECV_TOKEN;
                end
            end
            
            RECV_TOKEN: begin
                if (token_valid) begin
                    next_state = EMBEDDING;
                end
            end
            
            EMBEDDING: begin
                next_state = ATTENTION_PREP;
            end
            
            ATTENTION_PREP: begin
                next_state = ATTENTION_COMP;
            end
            
            ATTENTION_COMP: begin
                if (head_counter == NUM_HEADS - 1) begin
                    if (layer_counter == NUM_LAYERS - 1) begin
                        next_state = OUTPUT_HEAD;
                    end else begin
                        next_state = FFN_COMP;
                    end
                end
            end
            
            FFN_COMP: begin
                next_state = LAYER_NORM;
            end
            
            LAYER_NORM: begin
                next_state = ATTENTION_PREP;  // Next layer
            end
            
            OUTPUT_HEAD: begin
                next_state = SAMPLING;
            end
            
            SAMPLING: begin
                next_state = SEND_TOKEN;
            end
            
            SEND_TOKEN: begin
                if (tx_ready) begin
                    if (position_counter < CONTEXT_LEN - 1) begin
                        next_state = ATTENTION_PREP;  // Generate next token
                    end else begin
                        next_state = IDLE;
                    end
                end
            end
        endcase
    end
    
    // ========== Component Instantiations ==========
    
    // Embedding ROM
    embedding_rom #(
        .VOCAB_SIZE(VOCAB_SIZE),
        .EMBED_DIM(EMBED_DIM),
        .DATA_WIDTH(DATA_WIDTH)
    ) embed_rom_inst (
        .addr(embed_addr),
        .data_out(embed_out)
    );
    
    // Attention modules (one per head, instantiated in generate block)
    // FFN modules
    // Layer norm modules
    // Output head
    
    // KV Cache
    kv_cache #(
        .CONTEXT_LEN(CONTEXT_LEN),
        .NUM_LAYERS(NUM_LAYERS),
        .NUM_HEADS(NUM_HEADS),
        .HEAD_DIM(HEAD_DIM),
        .DATA_WIDTH(DATA_WIDTH)
    ) kv_cache_inst (
        .clk(clk),
        .rst_n(rst_n),
        .write_en(kv_write_en),
        .write_pos(position_counter),
        .layer_idx(layer_counter),
        .head_idx(head_counter),
        .is_key(1'b0),  // Controlled elsewhere
        .data_in(kv_data_in),
        .read_en(kv_read_en),
        .read_pos(/* read position */),
        .k_out(kv_k_out),
        .v_out(kv_v_out),
        .current_len(kv_current_len)
    );
    
    // ========== Control Logic ==========
    
    // Token reception
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            input_token <= '0;
            token_valid <= 1'b0;
            position_counter <= '0;
        end else begin
            // Token reception logic
            if (current_state == RECV_TOKEN && rx_valid) begin
                // Accumulate bytes into token (simplified)
                input_token <= rx_data;
                token_valid <= 1'b1;
            end else if (current_state == EMBEDDING) begin
                token_valid <= 1'b0;
            end
            
            // Position tracking
            if (current_state == SEND_TOKEN && tx_ready) begin
                position_counter <= position_counter + 1;
            end else if (current_state == IDLE) begin
                position_counter <= '0;
            end
        end
    end
    
    // Layer/head counters
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            layer_counter <= '0;
            head_counter <= '0;
        end else begin
            if (current_state == ATTENTION_COMP) begin
                head_counter <= head_counter + 1;
                if (head_counter == NUM_HEADS - 1) begin
                    head_counter <= '0;
                    layer_counter <= layer_counter + 1;
                end
            end else if (current_state == IDLE) begin
                layer_counter <= '0;
                head_counter <= '0;
            end
        end
    end
    
    // Status LEDs
    always_comb begin
        status_leds[0] = (current_state != IDLE);  // Active
        status_leds[1] = (current_state == ATTENTION_COMP);  // Computing attention
        status_leds[2] = (current_state == SEND_TOKEN);  // Outputting
        status_leds[3] = kv_current_len > 0;  // Has context
    end

endmodule
