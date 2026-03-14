// RAU Testbench
module rau_tb;
    // Parameters
    parameter int WIDTH = 8;
    parameter int ACC_WIDTH = 24;
    parameter int WEIGHT_WIDTH = 2;

    // Signals
    logic clk;
    logic rst_n;
    logic valid_in;
    logic ready_out;
    logic [WIDTH-1:0] activation_in;
    logic [WEIGHT_WIDTH-1:0] weight_in;
    logic valid_out;
    logic [ACC_WIDTH-1:0] result_out;

    // DUT
    rau rau_dut (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .ready_out(ready_out),
        .activation_in(activation_in),
        .weight_in(weight_in),
        .valid_out(valid_out),
        .result_out(result_out)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Reset
    initial begin
        rst_n = 0;
        #10 rst_n = 1;
    end

    // Stimulus Task
    task stimulus(input logic [WIDTH-1:0] activation, input logic [WEIGHT_WIDTH-1:0] weight);
        @(posedge clk);
        activation_in <= activation;
        weight_in <= weight;
        valid_in <= 1;
        @(posedge clk);
        valid_in <= 0;
        @(posedge ready_out);
    endtask

    // Scoreboard
    logic [ACC_WIDTH-1:0] expected_result;
    logic [ACC_WIDTH-1:0] actual_result;

    always @(posedge clk) begin
        if (valid_out) begin
            actual_result = result_out;
            if (actual_result !== expected_result) begin
                $error("Mismatch: expected %d, actual %d", expected_result, actual_result);
            end
        end
    end

    // Test Scenarios
    initial begin
        // Basic Ternary Operations
        expected_result = 0;
        stimulus(8'd10, 2'b00); // (+1)*a
        expected_result = 10;
        stimulus(8'd10, 2'b01); // (-1)*a
        expected_result = -10;
        stimulus(8'd10, 2'b10); // 0*a
        expected_result = -10;

        // Accumulation Sequence with Saturation
        expected_result = -10;
        stimulus(8'd20, 2'b01); // (-1)*a
        expected_result = -30;
        stimulus(8'd30, 2'b01); // (-1)*a
        expected_result = -60;
        stimulus(8'd40, 2'b01); // (-1)*a
        expected_result = -100; // Saturation

        // Pipeline Behavior Verification
        expected_result = -100;
        stimulus(8'd10, 2'b00); // (+1)*a
        expected_result = -90;
        stimulus(8'd20, 2'b00); // (+1)*a
        expected_result = -70;
        stimulus(8'd30, 2'b00); // (+1)*a
        expected_result = -40;

        // Back-to-Back Transactions
        expected_result = -40;
        stimulus(8'd10, 2'b00); // (+1)*a
        stimulus(8'd20, 2'b00); // (+1)*a
        expected_result = -10;
        stimulus(8'd30, 2'b00); // (+1)*a
        expected_result = 20;

        // Idle Cycles between Operations
        expected_result = 20;
        @(posedge clk);
        @(posedge clk);
        stimulus(8'd10, 2'b00); // (+1)*a
        expected_result = 30;

        // Reset Behavior
        rst_n = 0;
        @(posedge clk);
        rst_n = 1;
        expected_result = 0;

        // Maximum Accumulator Value
        expected_result = 0;
        for (int i = 0; i < 2**ACC_WIDTH-1; i++) begin
            stimulus(8'd1, 2'b00); // (+1)*a
        end
        expected_result = 2**ACC_WIDTH-1;

        // Minimum Accumulator Value (Negative Saturation)
        expected_result = 2**ACC_WIDTH-1;
        for (int i = 0; i < 2**ACC_WIDTH-1; i++) begin
            stimulus(8'd1, 2'b01); // (-1)*a
        end
        expected_result = -2**ACC_WIDTH+1;
    end

    // Coverage Collection
    covergroup cg @(posedge clk);
        coverpoint valid_in;
        coverpoint ready_out;
        coverpoint valid_out;
        coverpoint activation_in;
        coverpoint weight_in;
        coverpoint result_out;
    endgroup

    // Assertions for Protocol Checking
    assert property (@(posedge clk) disable iff (!rst_n) (valid_in |-> ready_out));
    assert property (@(posedge clk) disable iff (!rst_n) (valid_out |-> !ready_out));

endmodule