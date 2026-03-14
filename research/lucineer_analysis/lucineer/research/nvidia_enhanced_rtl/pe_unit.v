// Processing Element for 32x32 systolic array
// Target: 28nm, 1GHz, <1mW per PE

module PE (
    // Input ports
    input  logic clk, rst_n,
    input  logic [31:0] weight,
    input  logic [31:0] data_n, data_s, data_e, data_w,
    input  logic sleep, bypass,
    // Output ports
    output logic [31:0] result_n, result_s, result_e, result_w,
    output logic active
);

// Activation register
logic [31:0] activation;
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        activation <= 32'd0;
    end else if (!sleep) begin
        activation <= data_e;
    end
end

// Partial sum register
logic [31:0] partial_sum;
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        partial_sum <= 32'd0;
    end else if (!sleep) begin
        partial_sum <= partial_sum + (activation * weight);
    end
end

// RAU (Reusable Arithmetic Unit)
logic [31:0] rau_result;
always_comb begin
    rau_result = partial_sum + (activation * weight);
end

// Neighbor connections
always_comb begin
    result_n = rau_result;
    result_s = rau_result;
    result_e = rau_result;
    result_w = rau_result;
end

// Bypass mode
logic [31:0] bypass_result;
always_comb begin
    bypass_result = (bypass) ? data_e : rau_result;
end

// Activity monitor
always_comb begin
    active = (|activation) || (|partial_sum) || (|weight);
end

// Power optimization hints
// Use clock gating to reduce power consumption
logic clk_gated;
always_comb begin
    clk_gated = clk && !sleep;
end

// Use operand isolation to reduce power consumption
logic [31:0] isolated_weight;
always_comb begin
    isolated_weight = (active) ? weight : 32'd0;
end

// Timing constraints
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports data_n]
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports data_s]
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports data_e]
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports data_w]
// set_input_delay -clock clk 0.5 -max -add_delay [get_ports weight]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports result_n]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports result_s]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports result_e]
// set_output_delay -clock clk 0.5 -max -add_delay [get_ports result_w]
// set_multicycle_path -from [get_ports clk] -to [get_ports result_n] 2
// set_multicycle_path -from [get_ports clk] -to [get_ports result_s] 2
// set_multicycle_path -from [get_ports clk] -to [get_ports result_e] 2
// set_multicycle_path -from [get_ports clk] -to [get_ports result_w] 2

endmodule