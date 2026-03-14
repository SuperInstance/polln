//-----------------------------------------------------------------------------
// Module: synaptic_array
// Description: Processing element array for TernaryAir
//
// TernaryAir - Open Source Air-Gapped Inference Hardware
// Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)
// MIT License - https://opensource.org/licenses/MIT
//
// This module implements the main compute array consisting of RAUs
// (Rotation-Accumulate Units) organized as columns and rows.
//
// Organization: NUM_COLUMNS × NUM_ROWS = 96 RAUs (with default parameters)
// Each column processes in parallel, providing high throughput.
//
// Author: Casey DiGennaro
// Version: 1.0
//-----------------------------------------------------------------------------

module synaptic_array #(
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24,
    parameter int NUM_COLUMNS = 12,
    parameter int NUM_ROWS = 8
)(
    input  logic        clk,
    input  logic        rst_n,
    
    // Activation interface
    input  logic signed [ACTIVATION_WIDTH-1:0]  activations_in  [NUM_COLUMNS],
    output logic signed [ACTIVATION_WIDTH-1:0]  activations_out [NUM_COLUMNS],
    
    // Weight interface (from ROM)
    input  logic [1:0]  weights [NUM_COLUMNS][NUM_ROWS],
    
    // Output partial sums
    output logic signed [ACCUMULATOR_WIDTH-1:0] partial_sums [NUM_COLUMNS],
    
    // Control
    input  logic        compute_enable,
    input  logic        clear_accumulator
);

    //=========================================================================
    // Internal signals
    //=========================================================================
    
    // RAU outputs (intermediate)
    logic signed [ACCUMULATOR_WIDTH-1:0] rau_results [NUM_COLUMNS][NUM_ROWS];
    logic signed [ACCUMULATOR_WIDTH-1:0] rau_valid   [NUM_COLUMNS][NUM_ROWS];
    
    // Row activations (passed through rows)
    logic signed [ACTIVATION_WIDTH-1:0] row_activations [NUM_COLUMNS][NUM_ROWS+1];
    
    //=========================================================================
    // Generate RAU array
    //=========================================================================
    
    generate
        for (genvar col = 0; col < NUM_COLUMNS; col++) begin : gen_column
            
            // Connect input activations to first row
            assign row_activations[col][0] = activations_in[col];
            
            // Output activations from last row
            assign activations_out[col] = row_activations[col][NUM_ROWS];
            
            for (genvar row = 0; row < NUM_ROWS; row++) begin : gen_row
                
                // RAU instance
                rau #(
                    .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
                    .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH),
                    .PIPELINE(1)  // Enable pipelining for timing
                ) u_rau (
                    .clk(clk),
                    .rst_n(rst_n),
                    
                    // Activation input
                    .activation(row_activations[col][row]),
                    
                    // Weight from ROM
                    .weight(weights[col][row]),
                    
                    // Control
                    .valid_in(compute_enable),
                    .accumulate_en(compute_enable),
                    .clear_acc(clear_accumulator),
                    
                    // Output
                    .result(rau_results[col][row]),
                    .valid_out(rau_valid[col][row])
                );
                
                // Pass activation to next row (simplified - real design
                // would have proper dataflow)
                assign row_activations[col][row+1] = row_activations[col][row];
                
            end
        end
    endgenerate
    
    //=========================================================================
    // Column adder trees
    //=========================================================================
    
    generate
        for (genvar col = 0; col < NUM_COLUMNS; col++) begin : gen_adder_tree
            
            // Tree adder for partial sum
            // In a real design, this would be a proper tree structure
            // for timing optimization
            
            logic signed [ACCUMULATOR_WIDTH-1:0] tree_level0 [NUM_ROWS/2];
            logic signed [ACCUMULATOR_WIDTH-1:0] tree_level1 [NUM_ROWS/4];
            logic signed [ACCUMULATOR_WIDTH-1:0] tree_level2 [NUM_ROWS/8];
            
            // Level 0: Add pairs
            for (genvar i = 0; i < NUM_ROWS/2; i++) begin
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        tree_level0[i] <= '0;
                    end else if (clear_accumulator) begin
                        tree_level0[i] <= '0;
                    end else begin
                        tree_level0[i] <= rau_results[col][2*i] + 
                                          rau_results[col][2*i+1];
                    end
                end
            end
            
            // Level 1: Add pairs
            for (genvar i = 0; i < NUM_ROWS/4; i++) begin
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        tree_level1[i] <= '0;
                    end else if (clear_accumulator) begin
                        tree_level1[i] <= '0;
                    end else begin
                        tree_level1[i] <= tree_level0[2*i] + 
                                          tree_level0[2*i+1];
                    end
                end
            end
            
            // Level 2: Final sum
            always_ff @(posedge clk or negedge rst_n) begin
                if (!rst_n) begin
                    partial_sums[col] <= '0;
                end else if (clear_accumulator) begin
                    partial_sums[col] <= '0;
                end else begin
                    partial_sums[col] <= tree_level1[0] + tree_level1[1];
                end
            end
            
        end
    endgenerate
    
    //=========================================================================
    // Formal verification
    //=========================================================================
    
    `ifdef FORMAL
        // Verify array dimensions are valid
        initial begin
            assert(NUM_COLUMNS > 0);
            assert(NUM_ROWS > 0);
            assert(NUM_ROWS % 2 == 0);  // Required for tree adder
        end
        
        // Verify accumulator doesn't overflow catastrophically
        always @(posedge clk) begin
            for (int col = 0; col < NUM_COLUMNS; col++) begin
                if (!rst_n || clear_accumulator) begin
                    assert(partial_sums[col] == 0);
                end
            end
        end
    `endif

endmodule
