module mask_locked_weight_rom_tb;

    // Parameters
    localparam int WEIGHTS_PER_BYTE = 4;
    localparam int WEIGHTS_PER_WORD = 32 / WEIGHTS_PER_BYTE;
    localparam int WEIGHT_ROM_DEPTH = 512;
    localparam int WEIGHT_ROM_WIDTH = WEIGHTS_PER_WORD * WEIGHTS_PER_BYTE;
    localparam int ADDRESS_WIDTH = $clog2(WEIGHT_ROM_DEPTH);

    // Signals
    logic clk;
    logic [ADDRESS_WIDTH-1:0] addr;
    logic [WEIGHT_ROM_WIDTH-1:0] data_out;
    logic [WEIGHT_ROM_WIDTH-1:0] expected_data_out;

    // DUT
    mask_locked_weight_rom dut (
        .clk(clk),
        .addr(addr),
        .data_out(data_out)
    );

    // Testbench
    initial begin
        // Initialize signals
        clk = 0;
        addr = 0;

        // Test scenarios
        test_sequential_read();
        test_random_access();
        test_ecc_check();
        test_power_up_initialization();
        test_defect_detection();
    end

    // Test sequential read of all addresses
    task test_sequential_read();
        for (int i = 0; i < WEIGHT_ROM_DEPTH; i++) begin
            addr = i;
            @(posedge clk);
            expected_data_out = generate_expected_data(i);
            assert(data_out == expected_data_out) else $error("Sequential read failed at address %d", i);
        end
    endtask

    // Test random access patterns
    task test_random_access();
        for (int i = 0; i < 100; i++) begin
            addr = $urandom_range(WEIGHT_ROM_DEPTH-1, 0);
            @(posedge clk);
            expected_data_out = generate_expected_data(addr);
            assert(data_out == expected_data_out) else $error("Random access failed at address %d", addr);
        end
    endtask

    // Test ECC check (if implemented)
    task test_ecc_check();
        // Assuming ECC is implemented as a CRC-8 checksum
        logic [7:0] crc;
        for (int i = 0; i < WEIGHT_ROM_DEPTH; i++) begin
            addr = i;
            @(posedge clk);
            crc = calculate_crc(data_out);
            assert(crc == 0) else $error("ECC check failed at address %d", i);
        end
    endtask

    // Test power-up initialization
    task test_power_up_initialization();
        // Assuming power-up initialization is done by reading address 0
        addr = 0;
        @(posedge clk);
        expected_data_out = generate_expected_data(addr);
        assert(data_out == expected_data_out) else $error("Power-up initialization failed");
    endtask

    // Test defect detection patterns
    task test_defect_detection();
        // Assuming defect detection is done by reading a specific pattern
        logic [WEIGHT_ROM_WIDTH-1:0] defect_pattern;
        defect_pattern = '1;
        for (int i = 0; i < WEIGHT_ROM_DEPTH; i++) begin
            addr = i;
            @(posedge clk);
            assert(data_out != defect_pattern) else $error("Defect detection failed at address %d", i);
        end
    endtask

    // Generate expected data
    function logic [WEIGHT_ROM_WIDTH-1:0] generate_expected_data(int addr);
        // Assuming weights are packed 4 per byte
        logic [WEIGHT_ROM_WIDTH-1:0] data;
        for (int i = 0; i < WEIGHT_ROM_WIDTH / WEIGHTS_PER_BYTE; i++) begin
            data[i*WEIGHTS_PER_BYTE+:WEIGHTS_PER_BYTE] = $urandom_range(3, 0);
        end
        return data;
    endfunction

    // Calculate CRC-8 checksum
    function logic [7:0] calculate_crc(logic [WEIGHT_ROM_WIDTH-1:0] data);
        logic [7:0] crc;
        crc = 0;
        for (int i = 0; i < WEIGHT_ROM_WIDTH; i++) begin
            crc ^= data[i];
            for (int j = 0; j < 8; j++) begin
                if (crc[0]) begin
                    crc = crc >> 1 ^ 8'h07;
                end else begin
                    crc = crc >> 1;
                end
            end
        end
        return crc;
    endfunction

    // Clock generation
    always #5 clk = ~clk;

endmodule