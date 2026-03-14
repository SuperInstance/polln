/**
 * TernaryAir RTL Package
 * KV Cache Controller - Transformer Attention State Management
 * 
 * MIT License - Open Source Hardware
 * Author: Casey DiGennaro
 * Repository: github.com/superinstance/ternaryair
 * 
 * The KV Cache stores Key and Value vectors for transformer
 * attention during autoregressive generation. Unlike weights,
 * the cache is dynamic and stored in SRAM.
 * 
 * Memory Layout:
 *   [Layer 0 K] [Layer 0 V] [Layer 1 K] [Layer 1 V] ... [Layer N-1 V]
 *   Each K/V block is [HEADS × SEQ_LEN × HEAD_DIM] elements
 */

module kv_cache #(
    parameter int NUM_LAYERS = 24,
    parameter int NUM_HEADS = 16,
    parameter int HEAD_DIM = 128,
    parameter int MAX_SEQ_LEN = 4096,
    parameter int DATA_WIDTH = 4,     // INT4 for efficiency
    parameter int SRAM_ADDR_WIDTH = 24
)(
    input  logic                        clk,
    input  logic                        rst_n,
    
    // Write interface (append new K/V)
    input  logic                        write_en,
    input  logic [$clog2(NUM_LAYERS)-1:0] write_layer,
    input  logic                        write_is_value,  // 0=Key, 1=Value
    input  logic [$clog2(NUM_HEADS)-1:0] write_head,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] write_pos,
    input  logic [DATA_WIDTH-1:0]       write_data,
    
    // Read interface (attention access)
    input  logic                        read_en,
    input  logic [$clog2(NUM_LAYERS)-1:0] read_layer,
    input  logic                        read_is_value,
    input  logic [$clog2(NUM_HEADS)-1:0] read_head,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] read_pos,
    output logic [DATA_WIDTH-1:0]       read_data,
    output logic                        read_valid,
    
    // Sequence length tracking
    input  logic [$clog2(MAX_SEQ_LEN):0] current_seq_len,
    output logic                        cache_full,
    
    // Cache management
    input  logic                        cache_clear
);

    // Calculate total cache size
    localparam int ELEMENTS_PER_LAYER = NUM_HEADS * MAX_SEQ_LEN * HEAD_DIM * 2; // K + V
    localparam int TOTAL_ELEMENTS = NUM_LAYERS * ELEMENTS_PER_LAYER;
    
    // Address calculation
    function automatic [SRAM_ADDR_WIDTH-1:0] calc_addr(
        input logic [$clog2(NUM_LAYERS)-1:0] layer,
        input logic is_value,
        input logic [$clog2(NUM_HEADS)-1:0] head,
        input logic [$clog2(MAX_SEQ_LEN)-1:0] pos
    );
        // Address = layer_offset + kv_offset + head_offset + pos
        logic [SRAM_ADDR_WIDTH-1:0] addr;
        addr = layer * ELEMENTS_PER_LAYER;
        addr = addr + (is_value ? (ELEMENTS_PER_LAYER/2) : 0);
        addr = addr + head * MAX_SEQ_LEN * HEAD_DIM;
        addr = addr + pos * HEAD_DIM;
        return addr;
    endfunction
    
    // Dual-port SRAM interface (simplified)
    logic [SRAM_ADDR_WIDTH-1:0] write_addr, read_addr;
    logic sram_we, sram_re;
    
    assign write_addr = calc_addr(write_layer, write_is_value, write_head, write_pos);
    assign read_addr = calc_addr(read_layer, read_is_value, read_head, read_pos);
    assign sram_we = write_en;
    assign sram_re = read_en;
    
    // SRAM instance (would be replaced with actual SRAM macro)
    // Using distributed RAM for simulation
    (* ram_style = "block" *) logic [DATA_WIDTH-1:0] sram [TOTAL_ELEMENTS];
    
    // Write port
    always_ff @(posedge clk) begin
        if (sram_we) begin
            sram[write_addr] <= write_data;
        end
    end
    
    // Read port
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            read_data <= '0;
            read_valid <= 1'b0;
        end else begin
            if (sram_re) begin
                read_data <= sram[read_addr];
                read_valid <= 1'b1;
            end else begin
                read_valid <= 1'b0;
            end
        end
    end
    
    // Cache status
    assign cache_full = (current_seq_len >= MAX_SEQ_LEN);
    
    // Cache clear
    integer i;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || cache_clear) begin
            for (i = 0; i < TOTAL_ELEMENTS; i++) begin
                sram[i] <= '0;
            end
        end
    end

endmodule

/**
 * KV Cache Manager
 * High-level interface for KV cache operations
 */
module kv_cache_manager #(
    parameter int NUM_LAYERS = 24,
    parameter int NUM_HEADS = 16,
    parameter int HEAD_DIM = 128,
    parameter int MAX_SEQ_LEN = 4096
)(
    input  logic                        clk,
    input  logic                        rst_n,
    
    // Token-level interface
    input  logic                        new_token_en,
    input  logic [127:0]                new_key,    // Packed key vector
    input  logic [127:0]                new_value,  // Packed value vector
    input  logic [$clog2(NUM_LAYERS)-1:0] target_layer,
    
    // Attention interface
    input  logic                        attention_en,
    input  logic [$clog2(NUM_LAYERS)-1:0] attn_layer,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] attn_pos,
    output logic [127:0]                attn_key,
    output logic [127:0]                attn_value,
    
    // Status
    output logic [$clog2(MAX_SEQ_LEN):0] seq_len,
    output logic                        cache_full
);

    // Current sequence length
    logic [$clog2(MAX_SEQ_LEN):0] seq_len_reg;
    assign seq_len = seq_len_reg;
    
    // KV Cache instance
    kv_cache #(
        .NUM_LAYERS(NUM_LAYERS),
        .NUM_HEADS(NUM_HEADS),
        .HEAD_DIM(HEAD_DIM),
        .MAX_SEQ_LEN(MAX_SEQ_LEN)
    ) kv_cache_inst (
        .clk(clk),
        .rst_n(rst_n),
        .write_en(new_token_en),
        .write_layer(target_layer),
        .write_is_value(1'b0), // Simplified
        .write_head('0),
        .write_pos(seq_len_reg),
        .write_data('0), // Would be unpacked from new_key/new_value
        .read_en(attention_en),
        .read_layer(attn_layer),
        .read_is_value(1'b0),
        .read_head('0),
        .read_pos(attn_pos),
        .read_data(), // Would be packed into attn_key/attn_value
        .read_valid(),
        .current_seq_len(seq_len_reg),
        .cache_full(cache_full),
        .cache_clear('0)
    );
    
    // Sequence length management
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            seq_len_reg <= '0;
        end else if (new_token_en && !cache_full) begin
            seq_len_reg <= seq_len_reg + 1;
        end
    end

endmodule
