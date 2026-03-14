/**
 * TernaryAir RTL Package
 * Synaptic Array - Parallel RAU Processing Element Array
 * 
 * MIT License - Open Source Hardware
 * Author: Casey DiGennaro
 * Repository: github.com/superinstance/ternaryair
 * 
 * The Synaptic Array organizes multiple RAU instances into a
 * systolic structure for parallel matrix-vector multiplication.
 * Weights are mask-locked into metal routing during fabrication.
 */

module synaptic_array #(
    parameter int NUM_ROWS = 256,
    parameter int NUM_COLS = 256,
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24
)(
    input  logic                                 clk,
    input  logic                                 rst_n,
    
    // Column-wise activation input (one per column)
    input  logic [ACTIVATION_WIDTH-1:0]          activations [NUM_COLS],
    input  logic                                 activation_valid,
    
    // Row-wise weight encodings (mask-locked in metal, parametric for simulation)
    // In production, these would be hardwired routing patterns
    input  logic [1:0]                           weights [NUM_ROWS][NUM_COLS],
    
    // Control signals
    input  logic                                 compute_en,
    input  logic                                 row_rst [NUM_ROWS],
    
    // Row-wise outputs
    output logic [ACCUMULATOR_WIDTH-1:0]         results [NUM_ROWS],
    output logic                                 results_valid
);

    // Internal accumulator registers (one per row)
    logic [ACCUMULATOR_WIDTH-1:0] accumulators [NUM_ROWS];
    logic [ACCUMULATOR_WIDTH-1:0] partial_sums [NUM_ROWS][NUM_COLS];
    
    // Generate RAU array
    generate
        for (genvar row = 0; row < NUM_ROWS; row++) begin : gen_rows
            // First column: initialize accumulator
            rau #(
                .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
                .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH)
            ) rau_first (
                .clk(clk),
                .rst_n(rst_n),
                .activation(activations[0]),
                .activation_valid(activation_valid),
                .weight(weights[row][0]),
                .accumulate_en(compute_en),
                .accumulate_rst(row_rst[row]),
                .result(partial_sums[row][0]),
                .result_valid()
            );
            
            // Remaining columns: accumulate
            for (genvar col = 1; col < NUM_COLS; col++) begin : gen_cols
                // Partial sum accumulator
                always_ff @(posedge clk or negedge rst_n) begin
                    if (!rst_n) begin
                        partial_sums[row][col] <= '0;
                    end else if (row_rst[row]) begin
                        partial_sums[row][col] <= '0;
                    end else if (compute_en) begin
                        // Add current RAU output to running partial sum
                        logic [ACTIVATION_WIDTH:0] rotated;
                        case (weights[row][col])
                            2'b00: rotated = '0;
                            2'b01: rotated = {activations[col][ACTIVATION_WIDTH-1], activations[col]};
                            2'b10: rotated = -{activations[col][ACTIVATION_WIDTH-1], activations[col]};
                            default: rotated = '0;
                        endcase
                        partial_sums[row][col] <= partial_sums[row][col-1] + $signed(rotated);
                    end
                end
            end
        end
    endgenerate
    
    // Output assignment (last column of each row)
    generate
        for (genvar row = 0; row < NUM_ROWS; row++) begin : gen_output
            assign results[row] = partial_sums[row][NUM_COLS-1];
        end
    endgenerate
    
    assign results_valid = compute_en;

endmodule
