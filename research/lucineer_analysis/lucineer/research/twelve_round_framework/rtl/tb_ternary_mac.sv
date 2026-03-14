// Ternary MAC Unit Testbench
module ternary_mac_tb;

    // Parameters
    parameter WIDTH = 8;
    parameter CLOCK_PERIOD = 10;

    // Signals
    logic clk;
    logic rst_n;
    logic [WIDTH-1:0] a;
    logic [WIDTH-1:0] b;
    logic [WIDTH-1:0] c;
    logic [WIDTH-1:0] result;
    logic [WIDTH-1:0] expected_result;

    // DUT
    ternary_mac u_dut (
        .clk(clk),
        .rst_n(rst_n),
        .a(a),
        .b(b),
        .c(c),
        .result(result)
    );

    // Clock Generation
    initial begin
        clk = 0;
        forever #(CLOCK_PERIOD/2) clk = ~clk;
    end

    // Reset Generation
    initial begin
        rst_n = 0;
        #(CLOCK_PERIOD) rst_n = 1;
    end

    // Test Cases
    initial begin
        // Test Case 1: a + b + c
        a = 8'd10;
        b = 8'd20;
        c = 8'd30;
        expected_result = 8'd60;
        #(CLOCK_PERIOD) check_result();

        // Test Case 2: a - b + c
        a = 8'd50;
        b = 8'd20;
        c = 8'd30;
        expected_result = 8'd60;
        #(CLOCK_PERIOD) check_result();

        // Test Case 3: a + b - c
        a = 8'd50;
        b = 8'd20;
        c = 8'd30;
        expected_result = 8'd40;
        #(CLOCK_PERIOD) check_result();

        // Test Case 4: a - b - c
        a = 8'd50;
        b = 8'd20;
        c = 8'd30;
        expected_result = 8'd0;
        #(CLOCK_PERIOD) check_result();

        // Test Case 5: a + 0 + c
        a = 8'd50;
        b = 8'd0;
        c = 8'd30;
        expected_result = 8'd80;
        #(CLOCK_PERIOD) check_result();

        // Test Case 6: a - 0 + c
        a = 8'd50;
        b = 8'd0;
        c = 8'd30;
        expected_result = 8'd80;
        #(CLOCK_PERIOD) check_result();

        // Test Case 7: a + b + 0
        a = 8'd50;
        b = 8'd20;
        c = 8'd0;
        expected_result = 8'd70;
        #(CLOCK_PERIOD) check_result();

        // Test Case 8: a - b + 0
        a = 8'd50;
        b = 8'd20;
        c = 8'd0;
        expected_result = 8'd30;
        #(CLOCK_PERIOD) check_result();

        // Test Case 9: a + 0 - c
        a = 8'd50;
        b = 8'd0;
        c = 8'd30;
        expected_result = 8'd20;
        #(CLOCK_PERIOD) check_result();

        // Test Case 10: a - 0 - c
        a = 8'd50;
        b = 8'd0;
        c = 8'd30;
        expected_result = 8'd20;
        #(CLOCK_PERIOD) check_result();

        $finish;
    end

    // Check Result
    task check_result();
        if (result !== expected_result) begin
            $error("Result mismatch: expected %d, got %d", expected_result, result);
        end
    endtask

    // Coverage Collection
    covergroup ternary_mac_cg @(posedge clk);
        coverpoint a;
        coverpoint b;
        coverpoint c;
        coverpoint result;
    endgroup

    // Assertions
    assert property (@(posedge clk) rst_n |-> result == 0);
    assert property (@(posedge clk) !rst_n |-> result == 0);

endmodule