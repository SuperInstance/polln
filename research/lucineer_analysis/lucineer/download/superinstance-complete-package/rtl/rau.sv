/**
 * TernaryAir RTL Package
 * Rotation-Accumulate Unit (RAU) - Simplified Module
 * 
 * MIT License - Open Source Hardware
 * Author: Casey DiGennaro
 * Repository: github.com/superinstance/ternaryair
 */

module rau #(
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24
)(
    input  logic                        clk,
    input  logic                        rst_n,
    input  logic [ACTIVATION_WIDTH-1:0] activation,
    input  logic                        activation_valid,
    input  logic [1:0]                  weight,
    input  logic                        accumulate_en,
    input  logic                        accumulate_rst,
    output logic [ACCUMULATOR_WIDTH-1:0] result,
    output logic                        result_valid
);

    logic [ACTIVATION_WIDTH:0] rotated;
    logic [ACCUMULATOR_WIDTH-1:0] accumulator;

    always_comb begin
        case (weight)
            2'b00: rotated = '0;
            2'b01: rotated = {activation[ACTIVATION_WIDTH-1], activation};
            2'b10: rotated = -{activation[ACTIVATION_WIDTH-1], activation};
            default: rotated = '0;
        endcase
    end

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accumulator <= '0;
        end else if (accumulate_rst) begin
            accumulator <= '0;
        end else if (accumulate_en) begin
            accumulator <= accumulator + $signed(rotated);
        end
    end

    assign result = accumulator;
    assign result_valid = accumulate_en;

endmodule

/**
 * Synaptic Array - Parallel RAU Array
 * Simplified implementation for simulation
 */
module synaptic_array #(
    parameter int NUM_ROWS = 256,
    parameter int NUM_COLS = 256,
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24
)(
    input  logic                        clk,
    input  logic                        rst_n,
    input  logic [ACTIVATION_WIDTH-1:0] activations [NUM_COLS],
    input  logic                        activation_valid,
    input  logic [1:0]                  weights [NUM_ROWS][NUM_COLS],
    input  logic                        compute_en,
    input  logic                        row_rst [NUM_ROWS],
    output logic [ACCUMULATOR_WIDTH-1:0] results [NUM_ROWS],
    output logic                        results_valid
);

    logic [ACCUMULATOR_WIDTH-1:0] accumulators [NUM_ROWS];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (int r = 0; r < NUM_ROWS; r++) begin
                accumulators[r] <= '0;
            end
        end else if (compute_en) begin
            for (int r = 0; r < NUM_ROWS; r++) begin
                if (row_rst[r]) begin
                    accumulators[r] <= '0;
                end else begin
                    for (int c = 0; c < NUM_COLS; c++) begin
                        logic [ACTIVATION_WIDTH:0] rotated;
                        case (weights[r][c])
                            2'b00: rotated = '0;
                            2'b01: rotated = {activations[c][ACTIVATION_WIDTH-1], activations[c]};
                            2'b10: rotated = -{activations[c][ACTIVATION_WIDTH-1], activations[c]};
                            default: rotated = '0;
                        endcase
                        accumulators[r] <= accumulators[r] + $signed(rotated);
                    end
                end
            end
        end
    end

    assign results = accumulators;
    assign results_valid = compute_en;

endmodule
