// Advanced Processing Element (PE) with Ternary Accumulate, Power Gating, Clock Gating, Bypass Mode, and Sleep Mode

module advanced_pe(
    input  logic clk,
    input  logic rst_n,
    input  logic[1:0] op,
    input  logic[31:0] a,
    input  logic[31:0] b,
    input  logic bypass_en,
    input  logic sleep_en,
    output logic[31:0] result,
    output logic activity_cnt
);

// Ternary Accumulate Logic
logic[31:0] acc_result;
logic[1:0] acc_op;
logic acc_en;

always_comb begin
    case (op)
        2'b00: acc_op = 2'b00; // Add
        2'b01: acc_op = 2'b01; // Subtract
        2'b10: acc_op = 2'b10; // Multiply
        default: acc_op = 2'b00; // Default to Add
    endcase
end

always_comb begin
    case (acc_op)
        2'b00: acc_result = a + b;
        2'b01: acc_result = a - b;
        2'b10: acc_result = a * b;
        default: acc_result = a + b;
    endcase
end

// Power Gating Logic
logic power_gate_en;
logic clock_gate_en;

always_comb begin
    if (sleep_en) begin
        power_gate_en = 1'b0;
        clock_gate_en = 1'b0;
    end else begin
        power_gate_en = 1'b1;
        clock_gate_en = 1'b1;
    end
end

// Clock Gating Logic
logic gated_clk;
always_comb begin
    gated_clk = clock_gate_en ? clk : 1'b0;
end

// Bypass Mode Logic
logic bypass_result;
always_comb begin
    if (bypass_en) begin
        bypass_result = a;
    end else begin
        bypass_result = acc_result;
    end
end

// Activity Counter Logic
logic activity_cnt_en;
always_ff @(posedge gated_clk or negedge rst_n) begin
    if (!rst_n) begin
        activity_cnt <= 1'b0;
    end else if (activity_cnt_en) begin
        activity_cnt <= 1'b1;
    end else begin
        activity_cnt <= 1'b0;
    end
end

// Output Logic
always_comb begin
    if (power_gate_en) begin
        result = bypass_result;
    end else begin
        result = 32'b0;
    end
end

// Activity Counter Enable Logic
always_comb begin
    if (power_gate_en && clock_gate_en) begin
        activity_cnt_en = 1'b1;
    end else begin
        activity_cnt_en = 1'b0;
    end
end

endmodule