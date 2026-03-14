// KV Cache Testbench

// Import the memory model
import kv_cache_pkg::*;

module kv_cache_tb;

  // Parameters
  localparam int KV_CACHE_SIZE = 32 * 1024; // 32KB
  localparam int KV_CACHE_ENTRIES = 256;
  localparam int KV_CACHE_DATA_WIDTH = 128;
  localparam int KV_CACHE_BANKS = 4;

  // Signals
  logic clk;
  logic rst_n;
  logic [KV_CACHE_DATA_WIDTH-1:0] data_in;
  logic [KV_CACHE_DATA_WIDTH-1:0] data_out;
  logic [KV_CACHE_ENTRIES-1:0] addr;
  logic write_en;
  logic read_en;
  logic bank_sel;
  logic power_gate_en;
  logic full;
  logic empty;

  // Memory model
  kv_cache_memory #(
    .KV_CACHE_SIZE(KV_CACHE_SIZE),
    .KV_CACHE_ENTRIES(KV_CACHE_ENTRIES),
    .KV_CACHE_DATA_WIDTH(KV_CACHE_DATA_WIDTH)
  ) kv_cache_memory_inst (
    .clk(clk),
    .rst_n(rst_n),
    .data_in(data_in),
    .data_out(data_out),
    .addr(addr),
    .write_en(write_en),
    .read_en(read_en),
    .bank_sel(bank_sel),
    .power_gate_en(power_gate_en),
    .full(full),
    .empty(empty)
  );

  // Testbench
  initial begin
    // Initialize signals
    clk = 0;
    rst_n = 0;
    data_in = 0;
    addr = 0;
    write_en = 0;
    read_en = 0;
    bank_sel = 0;
    power_gate_en = 0;

    // Reset sequence
    #10 rst_n = 1;
    #10 rst_n = 0;
    #10 rst_n = 1;

    // Test scenarios
    // 1. Sequential write and read
    seq_write_read_test();

    // 2. Circular buffer wrap-around
    circular_buffer_wrap_around_test();

    // 3. Bank switching
    bank_switching_test();

    // 4. Power gating while retaining data
    power_gating_test();

    // 5. Concurrent read/write
    concurrent_read_write_test();

    // 6. Full/empty conditions
    full_empty_conditions_test();

    // 7. Stress test with random patterns
    stress_test();
  end

  // Clock generator
  always #5 clk = ~clk;

  // Test scenario 1: Sequential write and read
  task seq_write_read_test();
    // Write data to cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      data_in = i * 128;
      write_en = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Read data from cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      read_en = 1;
      @(posedge clk);
      read_en = 0;
      assert(data_out == i * 128);
    end
  endtask

  // Test scenario 2: Circular buffer wrap-around
  task circular_buffer_wrap_around_test();
    // Write data to cache
    for (int i = 0; i < KV_CACHE_ENTRIES * 2; i++) begin
      addr = i % KV_CACHE_ENTRIES;
      data_in = i * 128;
      write_en = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Read data from cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      read_en = 1;
      @(posedge clk);
      read_en = 0;
      assert(data_out == (i + KV_CACHE_ENTRIES) * 128);
    end
  endtask

  // Test scenario 3: Bank switching
  task bank_switching_test();
    // Write data to bank 0
    for (int i = 0; i < KV_CACHE_ENTRIES / KV_CACHE_BANKS; i++) begin
      addr = i;
      data_in = i * 128;
      write_en = 1;
      bank_sel = 0;
      @(posedge clk);
      write_en = 0;
    end

    // Write data to bank 1
    for (int i = 0; i < KV_CACHE_ENTRIES / KV_CACHE_BANKS; i++) begin
      addr = i;
      data_in = i * 128 + 128;
      write_en = 1;
      bank_sel = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Read data from bank 0
    for (int i = 0; i < KV_CACHE_ENTRIES / KV_CACHE_BANKS; i++) begin
      addr = i;
      read_en = 1;
      bank_sel = 0;
      @(posedge clk);
      read_en = 0;
      assert(data_out == i * 128);
    end

    // Read data from bank 1
    for (int i = 0; i < KV_CACHE_ENTRIES / KV_CACHE_BANKS; i++) begin
      addr = i;
      read_en = 1;
      bank_sel = 1;
      @(posedge clk);
      read_en = 0;
      assert(data_out == i * 128 + 128);
    end
  endtask

  // Test scenario 4: Power gating while retaining data
  task power_gating_test();
    // Write data to cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      data_in = i * 128;
      write_en = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Power gate the cache
    power_gate_en = 1;
    @(posedge clk);
    power_gate_en = 0;

    // Read data from cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      read_en = 1;
      @(posedge clk);
      read_en = 0;
      assert(data_out == i * 128);
    end
  endtask

  // Test scenario 5: Concurrent read/write
  task concurrent_read_write_test();
    // Write data to cache
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      data_in = i * 128;
      write_en = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Concurrent read and write
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      data_in = i * 128 + 128;
      write_en = 1;
      read_en = 1;
      @(posedge clk);
      write_en = 0;
      read_en = 0;
      assert(data_out == i * 128);
    end
  endtask

  // Test scenario 6: Full/empty conditions
  task full_empty_conditions_test();
    // Write data to cache until full
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      data_in = i * 128;
      write_en = 1;
      @(posedge clk);
      write_en = 0;
    end

    // Check full condition
    assert(full == 1);

    // Read data from cache until empty
    for (int i = 0; i < KV_CACHE_ENTRIES; i++) begin
      addr = i;
      read_en = 1;
      @(posedge clk);
      read_en = 0;
    end

    // Check empty condition
    assert(empty == 1);
  endtask

  // Test scenario 7: Stress test with random patterns
  task stress_test();
    // Generate random patterns
    for (int i = 0; i < 1000; i++) begin
      addr = $urandom_range(KV_CACHE_ENTRIES - 1, 0);
      data_in = $urandom_range(2**KV_CACHE_DATA_WIDTH - 1, 0);
      write_en = $urandom_range(1, 0);
      read_en = $urandom_range(1, 0);
      bank_sel = $urandom_range(KV_CACHE_BANKS - 1, 0);
      power_gate_en = $urandom_range(1, 0);

      @(posedge clk);
    end
  endtask

endmodule