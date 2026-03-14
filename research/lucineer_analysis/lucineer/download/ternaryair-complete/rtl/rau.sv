/**
 * RAU - Rotation-Accumulate Unit
 * 
 * The core innovation of TernaryAir. Replaces multiply-accumulate with
 * rotation-accumulate for ternary weights {-1, 0, +1}.
 * 
 * Author: Casey DiGennaro / SuperInstance.AI
 * License: MIT
 */

module rau #(
    parameter int DATA_WIDTH = 24,
    parameter int ACC_WIDTH  = 32
)(
    input  logic                    clk,
    input  logic                    rst_n,
    
    // Data input
    input  logic signed [DATA_WIDTH-1:0] activation,
    
    // Ternary weight: 00=+1, 01=0, 10=-1, 11=reserved
    input  logic [1:0]               weight,
    
    // Control
    input  logic                     accumulate_en,
    input  logic                     clear_acc,
    
    // Output
    output logic signed [ACC_WIDTH-1:0] result
);

    // Weight encoding
    localparam W_PLUS_ONE  = 2'b00;
    localparam W_ZERO      = 2'b01;
    localparam W_MINUS_ONE = 2'b10;
    
    // Internal signals
    logic signed [DATA_WIDTH:0] rotated;
    logic signed [ACC_WIDTH-1:0] accumulator;
    
    // Rotation logic - replaces multiplication
    always_comb begin
        case (weight)
            W_PLUS_ONE:  rotated = activation;           // Pass through
            W_ZERO:      rotated = '0;                   // Zero output
            W_MINUS_ONE: rotated = -activation;          // Negate
            default:     rotated = '0;
        endcase
    end
    
    // Accumulation
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accumulator <= '0;
        end else if (clear_acc) begin
            accumulator <= '0;
        end else if (accumulate_en) begin
            accumulator <= accumulator + rotated;
        end
    end
    
    assign result = accumulator;

endmodule
