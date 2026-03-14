// KV Cache Module
module kv_cache (
    input  logic clk,
    input  logic rst_n,
    input  logic [6:0]  addr,
    input  logic [127:0] data_in,
    input  logic we,
    output logic [127:0] data_out,
    output logic valid
);

// Power-gated bank enable
logic [3:0] bank_en;

// Circular buffer pointers
logic [7:0] head_ptr, tail_ptr;

// KV Cache Memory
logic [127:0] kv_cache_mem [255:0];

// Valid bits for each entry
logic [255:0] valid_bits;

// Power-gated bank enable logic
always_comb begin
    bank_en = 4'b0000;
    bank_en[addr[6:4]] = 1'b1;
end

// Circular buffer logic
always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        head_ptr <= 8'd0;
        tail_ptr <= 8'd0;
    end else if (we) begin
        head_ptr <= head_ptr + 8'd1;
        if (head_ptr == 8'd255) head_ptr <= 8'd0;
    end
end

// Write logic
always_ff @(posedge clk) begin
    if (we) begin
        kv_cache_mem[head_ptr] <= data_in;
        valid_bits[head_ptr] <= 1'b1;
    end
end

// Read logic
always_ff @(posedge clk) begin
    if (addr[6:0] == tail_ptr) begin
        data_out <= kv_cache_mem[tail_ptr];
        valid <= valid_bits[tail_ptr];
    end else begin
        data_out <= kv_cache_mem[addr[6:0]];
        valid <= valid_bits[addr[6:0]];
    end
end

// Power optimization hints
// synthesis attribute power_domain kv_cache_mem[255:0] power_domain_bank
// synthesis attribute power_domain valid_bits[255:0] power_domain_bank

// Timing constraints
// synthesis attribute clock_latency clk 0.5
// synthesis attribute clock_latency rst_n 0.5
// synthesis attribute clock_latency we 0.5
// synthesis attribute clock_latency addr 0.5
// synthesis attribute clock_latency data_in 0.5
// synthesis attribute clock_latency data_out 1.5
// synthesis attribute clock_latency valid 1.5

endmodule