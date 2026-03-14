/**
 * Synaptic Array - Parallel array of RAUs
 * 
 * Implements a column of RAUs for parallel matrix-vector multiplication.
 * Used in attention and feed-forward layers.
 * 
 * Author: Casey DiGennaro / SuperInstance.AI
 * License: MIT
 */

module synaptic_array #(
    parameter int NUM_RAUS    = 768,    // Number of parallel RAUs
    parameter int DATA_WIDTH  = 24,
    parameter int ACC_WIDTH   = 32,
    parameter int WEIGHT_SIZE = 2       // Ternary: 2 bits per weight
)(
    input  logic                                clk,
    input  logic                                rst_n,
    
    // Activation input bus (one per RAU)
    input  logic signed [DATA_WIDTH-1:0]        activations [NUM_RAUS],
    
    // Weight input bus (one per RAU)
    input  logic [WEIGHT_SIZE-1:0]              weights [NUM_RAUS],
    
    // Control signals
    input  logic                                accumulate_en,
    input  logic                                clear_acc,
    
    // Output - sum of all RAU outputs
    output logic signed [ACC_WIDTH-1:0]         result
);

    // Internal accumulator signals from each RAU
    logic signed [ACC_WIDTH-1:0] rau_results [NUM_RAUS];
    
    // Generate RAU instances
    genvar i;
    generate
        for (i = 0; i < NUM_RAUS; i++) begin : gen_raus
            rau #(
                .DATA_WIDTH(DATA_WIDTH),
                .ACC_WIDTH(ACC_WIDTH)
            ) rau_inst (
                .clk(clk),
                .rst_n(rst_n),
                .activation(activations[i]),
                .weight(weights[i]),
                .accumulate_en(accumulate_en),
                .clear_acc(clear_acc),
                .result(rau_results[i])
            );
        end
    endgenerate
    
    // Tree reduction for final sum
    // Note: In actual hardware, this would be a balanced adder tree
    // for optimal timing. Simplified here for clarity.
    
    localparam int TREE_STAGES = $clog2(NUM_RAUS);
    logic signed [ACC_WIDTH-1:0] sum_tree [NUM_RAUS];
    
    always_comb begin
        // First level: direct from RAUs
        for (int j = 0; j < NUM_RAUS; j++) begin
            sum_tree[j] = rau_results[j];
        end
        
        // Reduction (simplified - real implementation uses tree structure)
        result = '0;
        for (int k = 0; k < NUM_RAUS; k++) begin
            result = result + sum_tree[k];
        end
    end

endmodule
