module ternary_mac (
    input wire clk,
    input wire clk_en,
    input wire rst_n,
    input wire [7:0] activation,
    input wire [1:0] weight,
    input wire [23:0] acc_in,
    output reg [23:0] acc_out
);

    // Pipeline registers
    reg [7:0] act_reg;
    reg [1:0] weight_reg;
    reg [23:0] acc_reg;
    reg [23:0] mult_result;
    
    // Gated clock
    wire gated_clk;
    assign gated_clk = clk & clk_en;
    
    // Stage 1: Multiplication
    always @(posedge gated_clk or negedge rst_n) begin
        if (!rst_n) begin
            act_reg <= 8'b0;
            weight_reg <= 2'b0;
            acc_reg <= 24'b0;
            mult_result <= 24'b0;
        end else begin
            act_reg <= activation;
            weight_reg <= weight;
            acc_reg <= acc_in;
            
            // Ternary multiplication
            case (weight)
                2'b00:   mult_result <= 24'b0;                    // 0
                2'b01:   mult_result <= {{16{activation[7]}}, activation};  // +1
                2'b10:   mult_result <= -{{16{activation[7]}}, activation}; // -1
                default: mult_result <= 24'b0;                    // treat 11 as 0
            endcase
        end
    end
    
    // Stage 2: Accumulation
    always @(posedge gated_clk or negedge rst_n) begin
        if (!rst_n) begin
            acc_out <= 24'b0;
        end else begin
            acc_out <= acc_reg + mult_result;
        end
    end

endmodule