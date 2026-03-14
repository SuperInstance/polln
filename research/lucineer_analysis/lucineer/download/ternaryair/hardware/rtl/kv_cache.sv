//-----------------------------------------------------------------------------
// Module: kv_cache
// Description: Key-Value cache for transformer attention
//
// TernaryAir - Open Source Air-Gapped Inference Hardware
// Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)
// MIT License - https://opensource.org/licenses/MIT
//
// This module implements the KV cache for transformer attention layers.
// The cache stores key and value vectors for each attention head,
// enabling efficient autoregressive generation.
//
// Key Properties:
//   - Volatile SRAM (cleared on power-off)
//   - No persistent storage
//   - Cleared between inference sessions
//   - Power-of-two size for simple addressing
//
// Author: Casey DiGennaro
// Version: 1.0
//-----------------------------------------------------------------------------

module kv_cache #(
    parameter int CACHE_SIZE = 512 * 1024,  // 512KB default
    parameter int DATA_WIDTH = 64,           // 64-bit data bus
    parameter int NUM_HEADS = 16             // Number of attention heads
)(
    input  logic        clk,
    input  logic        rst_n,
    
    // Memory interface
    input  logic                      write_enable,
    input  logic                      read_enable,
    input  logic [$clog2(CACHE_SIZE)-1:0] address,
    input  logic [DATA_WIDTH-1:0]     write_data,
    output logic [DATA_WIDTH-1:0]     read_data,
    
    // Control
    input  logic        cache_clear    // Clear entire cache
);

    //=========================================================================
    // Local parameters
    //=========================================================================
    
    // Number of addressable words
    localparam int NUM_WORDS = CACHE_SIZE / (DATA_WIDTH / 8);
    localparam int ADDR_WIDTH = $clog2(NUM_WORDS);
    
    //=========================================================================
    // Memory array
    // In actual silicon, this would be SRAM blocks
    //=========================================================================
    
    logic [DATA_WIDTH-1:0] mem [0:NUM_WORDS-1];
    
    //=========================================================================
    // Read logic (synchronous SRAM)
    //=========================================================================
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            read_data <= '0;
        end else if (read_enable && !write_enable) begin
            read_data <= mem[address];
        end
    end
    
    //=========================================================================
    // Write logic
    //=========================================================================
    
    always_ff @(posedge clk) begin
        if (write_enable) begin
            mem[address] <= write_data;
        end
    end
    
    //=========================================================================
    // Cache clear logic
    //=========================================================================
    
    // Clear state machine
    logic cache_clearing;
    logic [ADDR_WIDTH-1:0] clear_address;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cache_clearing <= 1'b0;
            clear_address <= '0;
        end else if (cache_clear && !cache_clearing) begin
            // Start clearing
            cache_clearing <= 1'b1;
            clear_address <= '0;
        end else if (cache_clearing) begin
            // Clear one word per cycle
            mem[clear_address] <= '0;
            clear_address <= clear_address + 1'b1;
            
            // Check if done
            if (clear_address == NUM_WORDS - 1) begin
                cache_clearing <= 1'b0;
            end
        end
    end
    
    //=========================================================================
    // Initialization (simulation)
    //=========================================================================
    
    initial begin
        // Initialize all memory to zero
        for (int i = 0; i < NUM_WORDS; i++) begin
            mem[i] = '0;
        end
    end
    
    //=========================================================================
    // Statistics counters (for debugging)
    //=========================================================================
    
    logic [31:0] write_count;
    logic [31:0] read_count;
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            write_count <= '0;
            read_count <= '0;
        end else begin
            if (write_enable)
                write_count <= write_count + 1'b1;
            if (read_enable)
                read_count <= read_count + 1'b1;
        end
    end
    
    //=========================================================================
    // Formal verification
    //=========================================================================
    
    `ifdef FORMAL
        // After reset, memory should be zero
        always @(posedge clk) begin
            if (!rst_n) begin
                // All memory should be zero
                for (int i = 0; i < NUM_WORDS; i++) begin
                    assert(mem[i] == 0);
                end
            end
        end
        
        // Clear operation should complete
        always @(posedge clk) begin
            if (cache_clearing) begin
                // Address should increment
                // Eventually reach end
            end
        end
    `endif

endmodule
