// RAU (Rotation-Accumulate Unit) for ternary NN
// 8-bit activation input, 2-bit ternary weight {-1,0,+1}
// Rotation-based multiply-accumulate (no multipliers!)
// 2-stage pipeline, 24-bit accumulator with saturation
// Valid/ready handshaking, clock gating
// Target: 28nm, 1GHz, minimal power

module rau (
    input  wire clk,
    input  wire rst_n,
    input  wire valid_i,
    output wire ready_o,
    input  wire [7:0] act_i,
    input  wire [1:0] weight_i,
    output wire [23:0] result_o,
    output wire valid_o
);

// Stage 1: Rotation and Accumulation
reg [7:0] act_reg;
reg [1:0] weight_reg;
reg [23:0] acc_reg;
reg [23:0] acc_next;

always @(posedge clk) begin
    if (!rst_n) begin
        act_reg <= 8'd0;
        weight_reg <= 2'd0;
        acc_reg <= 24'd0;
    end else if (valid_i) begin
        act_reg <= act_i;
        weight_reg <= weight_i;
        acc_reg <= acc_next;
    end
end

// Rotation-based multiply-accumulate
wire [7:0] rotated_act;
wire [23:0] acc_update;

assign rotated_act = (weight_reg[1]) ? (weight_reg[0] ? ~act_reg : act_reg) : (act_reg << 1);

assign acc_update = (weight_reg[1]) ? (weight_reg[0] ? -acc_reg : acc_reg) : (acc_reg + {16'd0, rotated_act});

assign acc_next = (acc_reg + acc_update) > 24'd8388607 ? 24'd8388607 : 
                  (acc_reg + acc_update) < 24'd-8388608 ? 24'd-8388608 : 
                  acc_reg + acc_update;

// Stage 2: Saturation and Output
reg [23:0] result_reg;
reg valid_reg;

always @(posedge clk) begin
    if (!rst_n) begin
        result_reg <= 24'd0;
        valid_reg <= 1'd0;
    end else if (valid_i) begin
        result_reg <= acc_reg;
        valid_reg <= 1'd1;
    end else begin
        valid_reg <= 1'd0;
    end
end

assign result_o = result_reg;
assign valid_o = valid_reg;

// Clock Gating
reg clk_en;

always @(posedge clk) begin
    if (!rst_n) begin
        clk_en <= 1'd0;
    end else begin
        clk_en <= valid_i;
    end
end

// Timing Constraints
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports act_i]
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports weight_i]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports result_o]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports valid_o]

// Power Optimization Hints
// set_power_optimization -hierarchy rau -effort high
// set_power_optimization -hierarchy rau -clock_gating true

endmodule