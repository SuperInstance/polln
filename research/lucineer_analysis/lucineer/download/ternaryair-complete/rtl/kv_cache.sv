/**
 * KV Cache - Key-Value Cache Controller
 * 
 * Manages the KV cache for autoregressive generation.
 * Stores K and V vectors for all previous tokens.
 * 
 * Author: Casey DiGennaro / SuperInstance.AI
 * License: MIT
 */

module kv_cache #(
    parameter int CONTEXT_LEN  = 4096,    // Maximum context length
    parameter int NUM_LAYERS   = 24,      // Number of transformer layers
    parameter int NUM_HEADS    = 12,      // Number of attention heads
    parameter int HEAD_DIM     = 64,      // Dimension per head
    parameter int DATA_WIDTH   = 24       // Activation bit width
)(
    input  logic                            clk,
    input  logic                            rst_n,
    
    // Write interface (new token)
    input  logic                            write_en,
    input  logic [$clog2(CONTEXT_LEN)-1:0] write_pos,
    input  logic [$clog2(NUM_LAYERS)-1:0]  layer_idx,
    input  logic [$clog2(NUM_HEADS)-1:0]   head_idx,
    input  logic                            is_key,       // 1=K, 0=V
    input  logic signed [DATA_WIDTH-1:0]   data_in,
    
    // Read interface (attention computation)
    input  logic                            read_en,
    input  logic [$clog2(CONTEXT_LEN)-1:0] read_pos,
    output logic signed [DATA_WIDTH-1:0]   k_out,
    output logic signed [DATA_WIDTH-1:0]   v_out,
    
    // Status
    output logic [$clog2(CONTEXT_LEN):0]   current_len
);

    // Calculate total storage requirements
    localparam int ENTRIES_PER_POS = NUM_LAYERS * NUM_HEADS * 2;  // K and V for each head/layer
    localparam int ADDR_WIDTH = $clog2(CONTEXT_LEN * ENTRIES_PER_POS);
    
    // Dual-port SRAM for K and V storage
    
    logic [ADDR_WIDTH-1:0] write_addr;
    logic [ADDR_WIDTH-1:0] read_addr_k;
    logic [ADDR_WIDTH-1:0] read_addr_v;
    
    // Address calculation
    always_comb begin
        write_addr = (write_pos * ENTRIES_PER_POS) +
                     (layer_idx * NUM_HEADS * 2) +
                     (head_idx * 2) +
                     (is_key ? 0 : 1);
                     
        read_addr_k = (read_pos * ENTRIES_PER_POS) +
                      (layer_idx * NUM_HEADS * 2) +
                      (head_idx * 2);
                      
        read_addr_v = read_addr_k + 1;
    end
    
    // SRAM storage
    logic signed [DATA_WIDTH-1:0] sram [CONTEXT_LEN * ENTRIES_PER_POS];
    
    // Write port
    always_ff @(posedge clk) begin
        if (write_en) begin
            sram[write_addr] <= data_in;
        end
    end
    
    // Read port (1 cycle latency)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            k_out <= '0;
            v_out <= '0;
        end else if (read_en) begin
            k_out <= sram[read_addr_k];
            v_out <= sram[read_addr_v];
        end
    end
    
    // Track current sequence length
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_len <= '0;
        end else if (write_en && write_pos >= current_len) begin
            current_len <= write_pos + 1;
        end else if (write_pos == 0 && write_en) begin
            current_len <= 1;
        end
    end

endmodule
