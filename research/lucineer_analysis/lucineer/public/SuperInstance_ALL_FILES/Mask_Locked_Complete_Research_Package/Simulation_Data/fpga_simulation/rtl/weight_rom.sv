//-----------------------------------------------------------------------------
// Module: mask_locked_weight_rom
// Description: Weight storage using mask-defined metal patterns
//
// Key Innovation: Weights are encoded as via patterns in metal layers
//   - No SRAM needed for weight storage
//   - Zero power to maintain weights (non-volatile by definition)
//   - Zero access time (geometry IS the weight)
//   - Immutable = tamper-proof baseline for security
//
// Via Pattern Encoding for Ternary Weights:
//   +1: Via present (connection)
//    0: No via (open circuit)
//   -1: Via to complement (inverse connection)
//
// Author: SuperInstance.AI VP Manufacturing  
// Version: 1.0
//-----------------------------------------------------------------------------

module mask_locked_weight_rom #(
    parameter int NUM_TILES = 20,
    parameter int RAUS_PER_TILE = 256,
    parameter int NUM_LAYERS = 24,
    parameter int WEIGHT_BANKS = NUM_LAYERS * 4,  // Q, K, V, MLP per layer
    
    // Derived: Total weights = 20 tiles × 256 RAUs = 5120 weights per bank
    parameter int TOTAL_WEIGHTS = NUM_TILES * RAUS_PER_TILE
)(
    input  logic clk,
    input  logic [7:0] bank_select,
    output logic [NUM_TILES-1:0][RAUS_PER_TILE-1:0][1:0] weights_out
);

    //--------------------------------------------------------------------------
    // Ternary weight encoding
    //--------------------------------------------------------------------------
    
    localparam bit [1:0] W_PLUS_ONE  = 2'b00;  // +1
    localparam bit [1:0] W_ZERO      = 2'b01;  //  0
    localparam bit [1:0] W_MINUS_ONE = 2'b10;  // -1
    localparam bit [1:0] W_RESERVED  = 2'b11;  // Reserved
    
    //--------------------------------------------------------------------------
    // Weight Banks
    // In actual silicon, these would be physical via patterns
    // For simulation/FPGA, we use block RAM initialization
    //--------------------------------------------------------------------------
    
    // Weight memory: [bank][tile][rau]
    (* rom_style = "block" *) logic [1:0] weight_mem [0:WEIGHT_BANKS-1][0:NUM_TILES-1][0:RAUS_PER_TILE-1];
    
    //--------------------------------------------------------------------------
    // Initialize weights with pattern (simulating trained model)
    // In production: Load from trained BitNet model weights
    //--------------------------------------------------------------------------
    
    initial begin
        // Example: Initialize with structured pattern for testing
        // Real weights would come from model checkpoint
        
        for (int bank = 0; bank < WEIGHT_BANKS; bank++) begin
            for (int tile = 0; tile < NUM_TILES; tile++) begin
                for (int rau = 0; rau < RAUS_PER_TILE; rau++) begin
                    
                    // Initialize with pseudo-random ternary weights
                    // In production: Load actual model weights
                    case ((bank + tile + rau) % 3)
                        0: weight_mem[bank][tile][rau] = W_PLUS_ONE;
                        1: weight_mem[bank][tile][rau] = W_ZERO;
                        2: weight_mem[bank][tile][rau] = W_MINUS_ONE;
                    endcase
                end
            end
        end
        
        $display("[Weight ROM] Initialized %0d banks × %0d tiles × %0d RAUs = %0d weights",
                 WEIGHT_BANKS, NUM_TILES, RAUS_PER_TILE, 
                 WEIGHT_BANKS * NUM_TILES * RAUS_PER_TILE);
    end
    
    //--------------------------------------------------------------------------
    // Asynchronous read (combinational for weight access)
    // In mask-locked implementation, this is direct metal routing
    //--------------------------------------------------------------------------
    
    always_comb begin
        for (int t = 0; t < NUM_TILES; t++) begin
            for (int r = 0; r < RAUS_PER_TILE; r++) begin
                if (bank_select < WEIGHT_BANKS) begin
                    weights_out[t][r] = weight_mem[bank_select][t][r];
                end else begin
                    weights_out[t][r] = W_ZERO;  // Default to zero
                end
            end
        end
    end
    
    //--------------------------------------------------------------------------
    // Synthesis attributes for different targets
    //--------------------------------------------------------------------------
    
    // For Xilinx: Use BRAM
    (* ram_style = "block" *)
    
    // For Intel/Altera: Use M20K
    // altera_attribute = "-name RAM_BLOCK_TYPE M20K"

endmodule
