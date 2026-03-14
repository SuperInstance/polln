// pe_array_testbench.sv

// UVM-style testbench structure
import uvm_pkg::*;
`include "uvm_macros.svh"

// PE array module
module pe_array (
    input logic clk,
    input logic rst_n,

    // North, South, East, West data ports
    input logic [31:0] north_data,
    input logic [31:0] south_data,
    input logic [31:0] east_data,
    input logic [31:0] west_data,

    // Ternary weight input
    input logic [1:0] weight,

    // Partial sum input/output
    input logic [31:0] partial_sum_in,
    output logic [31:0] partial_sum_out,

    // Valid/ready handshaking
    input logic valid,
    output logic ready
);

    // PE array implementation
    // ...

endmodule

// Testbench module
module pe_array_testbench;
    // Clock and reset signals
    logic clk;
    logic rst_n;

    // North, South, East, West data ports
    logic [31:0] north_data;
    logic [31:0] south_data;
    logic [31:0] east_data;
    logic [31:0] west_data;

    // Ternary weight input
    logic [1:0] weight;

    // Partial sum input/output
    logic [31:0] partial_sum_in;
    logic [31:0] partial_sum_out;

    // Valid/ready handshaking
    logic valid;
    logic ready;

    // PE array instance
    pe_array pe_array_inst (
        .clk(clk),
        .rst_n(rst_n),

        .north_data(north_data),
        .south_data(south_data),
        .east_data(east_data),
        .west_data(west_data),

        .weight(weight),

        .partial_sum_in(partial_sum_in),
        .partial_sum_out(partial_sum_out),

        .valid(valid),
        .ready(ready)
    );

    // Testbench tasks
    task systolic_data_flow;
        // Systolic data flow (weight-stationary) test scenario
        // ...
    endtask

    task neighbor_to_neighbor_communication;
        // Neighbor-to-neighbor communication test scenario
        // ...
    endtask

    task full_array_computation;
        // Full array computation test scenario
        // ...
    endtask

    task power_gating_modes;
        // Power gating modes test scenario
        // ...
    endtask

    task sleep_wake_transitions;
        // Sleep/wake transitions test scenario
        // ...
    endtask

    task defect_bypass_testing;
        // Defect bypass testing test scenario
        // ...
    endtask

    // Testbench initial block
    initial begin
        // Initialize clock and reset signals
        clk = 0;
        rst_n = 0;

        // Initialize North, South, East, West data ports
        north_data = 0;
        south_data = 0;
        east_data = 0;
        west_data = 0;

        // Initialize ternary weight input
        weight = 0;

        // Initialize partial sum input/output
        partial_sum_in = 0;
        partial_sum_out = 0;

        // Initialize valid/ready handshaking
        valid = 0;
        ready = 0;

        // Run test scenarios
        systolic_data_flow();
        neighbor_to_neighbor_communication();
        full_array_computation();
        power_gating_modes();
        sleep_wake_transitions();
        defect_bypass_testing();

        // Dump waveform
        $dumpfile("pe_array_testbench.vcd");
        $dumpvars(0, pe_array_testbench);
    end

    // Clock generation
    always #10 clk = ~clk;

endmodule

// Coverage for activation patterns
class pe_array_coverage extends uvm_subscriber #(logic [31:0]);
    `uvm_component_utils(pe_array_coverage)

    // Coverage variables
    logic [31:0] north_data_cov;
    logic [31:0] south_data_cov;
    logic [31:0] east_data_cov;
    logic [31:0] west_data_cov;
    logic [1:0] weight_cov;
    logic [31:0] partial_sum_in_cov;
    logic [31:0] partial_sum_out_cov;
    logic valid_cov;
    logic ready_cov;

    // Coverage bins
    covergroup pe_array_coverage_cg @(posedge clk);
        // Coverage bins for North, South, East, West data ports
        coverpoint north_data_cov {
            bins north_data_bin[] = {[0:100]};
        }
        coverpoint south_data_cov {
            bins south_data_bin[] = {[0:100]};
        }
        coverpoint east_data_cov {
            bins east_data_bin[] = {[0:100]};
        }
        coverpoint west_data_cov {
            bins west_data_bin[] = {[0:100]};
        }

        // Coverage bins for ternary weight input
        coverpoint weight_cov {
            bins weight_bin[] = {[0:2]};
        }

        // Coverage bins for partial sum input/output
        coverpoint partial_sum_in_cov {
            bins partial_sum_in_bin[] = {[0:100]};
        }
        coverpoint partial_sum_out_cov {
            bins partial_sum_out_bin[] = {[0:100]};
        }

        // Coverage bins for valid/ready handshaking
        coverpoint valid_cov {
            bins valid_bin[] = {[0:1]};
        }
        coverpoint ready_cov {
            bins ready_bin[] = {[0:1]};
        }
    endgroup

    // Constructor
    function new(string name, uvm_component parent);
        super.new(name, parent);
        pe_array_coverage_cg = new();
    endfunction

    // Write function
    function void write(logic [31:0] t);
        north_data_cov = north_data;
        south_data_cov = south_data;
        east_data_cov = east_data;
        west_data_cov = west_data;
        weight_cov = weight;
        partial_sum_in_cov = partial_sum_in;
        partial_sum_out_cov = partial_sum_out;
        valid_cov = valid;
        ready_cov = ready;
        pe_array_coverage_cg.sample();
    endfunction
endclass