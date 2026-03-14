//-----------------------------------------------------------------------------
// Module: weight_rom
// Description: Mask-locked weight storage for TernaryAir
//
// TernaryAir - Open Source Air-Gapped Inference Hardware
// Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)
// MIT License - https://opensource.org/licenses/MIT
//
// This module implements the weight ROM using mask-locked via patterns.
// In actual silicon, weights are stored as physical metal via patterns:
//   - Via present     = +1 (connection)
//   - Via to VSS      = -1 (inverted connection)
//   - No via          =  0 (open circuit)
//
// For RTL simulation, we use a case statement with pre-defined weights.
// In production, this would be generated from the trained model.
//
// Security Properties:
//   - Cannot be read electronically (it's geometry, not data)
//   - Cannot be modified (it's solid metal patterns)
//   - Cannot be extracted without destructive analysis
//
// Author: Casey DiGennaro
// Version: 1.0
//-----------------------------------------------------------------------------

module weight_rom #(
    parameter int NUM_LAYERS = 24,
    parameter int HIDDEN_DIM = 1024,
    parameter int NUM_COLUMNS = 12,
    parameter int NUM_ROWS = 8
)(
    input  logic        clk,
    input  logic        rst_n,
    
    // Layer and column selection
    input  logic [5:0]  layer_select,    // Up to 64 layers
    input  logic [11:0] column_select,   // Column within layer
    
    // Weight output (ternary encoded)
    output logic [1:0]  weights [NUM_COLUMNS][NUM_ROWS],
    
    // Control
    input  logic        rom_enable
);

    //=========================================================================
    // Weight encoding
    //=========================================================================
    
    localparam bit [1:0] W_PLUS_ONE  = 2'b00;
    localparam bit [1:0] W_ZERO      = 2'b01;
    localparam bit [1:0] W_MINUS_ONE = 2'b10;
    
    //=========================================================================
    // Weight storage (simulation model)
    // In actual silicon, these become via patterns in metal layers 4-6
    //=========================================================================
    
    // For simulation, we use a ROM with pseudo-random weights
    // In production, these are generated from the trained model
    
    // Weight ROM - organized by layer, then column/row
    // Each entry is a 2-bit ternary weight
    
    // Note: In actual implementation, this would be synthesized as
    // via patterns, not as a readable ROM. The simulation model
    // approximates the behavior.
    
    logic [1:0] weight_memory [0:NUM_LAYERS-1][0:NUM_COLUMNS-1][0:NUM_ROWS-1];
    
    //=========================================================================
    // Initialize weights (simulation only)
    // In production, these would be mask-programmed
    //=========================================================================
    
    initial begin
        // Initialize with a deterministic pattern for simulation
        // This represents a trained ternary model
        
        for (int layer = 0; layer < NUM_LAYERS; layer++) begin
            for (int col = 0; col < NUM_COLUMNS; col++) begin
                for (int row = 0; row < NUM_ROWS; row++) begin
                    // Pseudo-random but deterministic weights
                    // In production, these come from model training
                    int seed = layer * 1000 + col * 100 + row;
                    int value = (seed * 1103515245 + 12345) % 3;
                    
                    case (value)
                        0: weight_memory[layer][col][row] = W_PLUS_ONE;
                        1: weight_memory[layer][col][row] = W_ZERO;
                        2: weight_memory[layer][col][row] = W_MINUS_ONE;
                    endcase
                end
            end
        end
    end
    
    //=========================================================================
    // ROM read logic
    //=========================================================================
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int col = 0; col < NUM_COLUMNS; col++) begin
                for (int row = 0; row < NUM_ROWS; row++) begin
                    weights[col][row] <= W_ZERO;
                end
            end
        end else if (rom_enable) begin
            // Read weights for selected layer and column
            for (int col = 0; col < NUM_COLUMNS; col++) begin
                for (int row = 0; row < NUM_ROWS; row++) begin
                    if (layer_select < NUM_LAYERS) begin
                        weights[col][row] <= weight_memory[layer_select][col][row];
                    end else begin
                        weights[col][row] <= W_ZERO;
                    end
                end
            end
        end
    end
    
    //=========================================================================
    // Synthesis directives
    //=========================================================================
    
    // In actual silicon synthesis, this would be:
    // 1. Converted to via patterns by the ROM generator
    // 2. Implemented in metal layers 4-6
    // 3. Not readable as data - only through computation
    
    // synthesis translate_off
    // Simulation-only code
    // synthesis translate_on
    
    //=========================================================================
    // Formal verification
    //=========================================================================
    
    `ifdef FORMAL
        // Weights are always valid ternary values
        always @(posedge clk) begin
            for (int col = 0; col < NUM_COLUMNS; col++) begin
                for (int row = 0; row < NUM_ROWS; row++) begin
                    assert(weights[col][row] != 2'b11);  // Reserved value
                end
            end
        end
        
        // ROM enables only when needed
        always @(posedge clk) begin
            if (!rom_enable) begin
                // Weights should be stable when disabled
            end
        end
    `endif

endmodule
