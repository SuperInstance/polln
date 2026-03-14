// KV Cache Module
module kv_cache (
    input  logic clk,
    input  logic rst_n,
    input  logic [127:0] data_in,
    input  logic [15:0] key_in,
    input  logic [15:0] value_in,
    input  logic write_en,
    input  logic read_en,
    output logic [127:0] data_out,
    output logic valid_out
);

// Parameters
parameter KV_CACHE_CAPACITY = 32 * 1024; // 32KB
parameter DATA_WIDTH = 128;
parameter KEY_WIDTH = 16;
parameter VALUE_WIDTH = 16;
parameter BANKS = 4;
parameter BANK_SIZE = KV_CACHE_CAPACITY / BANKS;

// Signals
logic [BANKS-1:0] bank_en;
logic [BANKS-1:0] bank_valid;
logic [BANKS-1:0] bank_power_gate;
logic [BANKS-1:0][DATA_WIDTH-1:0] bank_data_out;
logic [BANKS-1:0][KEY_WIDTH-1:0] bank_key_out;
logic [BANKS-1:0][VALUE_WIDTH-1:0] bank_value_out;

// Bank Module
module bank (
    input  logic clk,
    input  logic rst_n,
    input  logic en,
    input  logic power_gate,
    input  logic [DATA_WIDTH-1:0] data_in,
    input  logic [KEY_WIDTH-1:0] key_in,
    input  logic [VALUE_WIDTH-1:0] value_in,
    input  logic write_en,
    input  logic read_en,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic [KEY_WIDTH-1:0] key_out,
    output logic [VALUE_WIDTH-1:0] value_out,
    output logic valid
);

// Simple Run-Length Encoding (RLE) Compression
module rle_compressor (
    input  logic clk,
    input  logic rst_n,
    input  logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic compressed
);

// Circular Buffer for Streaming
module circular_buffer (
    input  logic clk,
    input  logic rst_n,
    input  logic [DATA_WIDTH-1:0] data_in,
    input  logic write_en,
    input  logic read_en,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic full,
    output logic empty
);

// Power-Gated Bank
module power_gated_bank (
    input  logic clk,
    input  logic rst_n,
    input  logic en,
    input  logic power_gate,
    input  logic [DATA_WIDTH-1:0] data_in,
    input  logic [KEY_WIDTH-1:0] key_in,
    input  logic [VALUE_WIDTH-1:0] value_in,
    input  logic write_en,
    input  logic read_en,
    output logic [DATA_WIDTH-1:0] data_out,
    output logic [KEY_WIDTH-1:0] key_out,
    output logic [VALUE_WIDTH-1:0] value_out,
    output logic valid
);

// KV Cache Implementation
genvar i;
generate
    for (i = 0; i < BANKS; i++) begin : bank_inst
        bank bank_inst (
            .clk(clk),
            .rst_n(rst_n),
            .en(bank_en[i]),
            .power_gate(bank_power_gate[i]),
            .data_in(data_in),
            .key_in(key_in),
            .value_in(value_in),
            .write_en(write_en),
            .read_en(read_en),
            .data_out(bank_data_out[i]),
            .key_out(bank_key_out[i]),
            .value_out(bank_value_out[i]),
            .valid(bank_valid[i])
        );
    end
endgenerate

// RLE Compression
rle_compressor rle_compressor_inst (
    .clk(clk),
    .rst_n(rst_n),
    .data_in(data_in),
    .data_out(data_out),
    .compressed()
);

// Circular Buffer
circular_buffer circular_buffer_inst (
    .clk(clk),
    .rst_n(rst_n),
    .data_in(data_in),
    .write_en(write_en),
    .read_en(read_en),
    .data_out(data_out),
    .full(),
    .empty()
);

// Power-Gated Bank
genvar j;
generate
    for (j = 0; j < BANKS; j++) begin : power_gated_bank_inst
        power_gated_bank power_gated_bank_inst (
            .clk(clk),
            .rst_n(rst_n),
            .en(bank_en[j]),
            .power_gate(bank_power_gate[j]),
            .data_in(data_in),
            .key_in(key_in),
            .value_in(value_in),
            .write_en(write_en),
            .read_en(read_en),
            .data_out(bank_data_out[j]),
            .key_out(bank_key_out[j]),
            .value_out(bank_value_out[j]),
            .valid(bank_valid[j])
        );
    end
endgenerate

// Output Logic
always_comb begin
    data_out = '0;
    valid_out = '0;
    for (int i = 0; i < BANKS; i++) begin
        if (bank_valid[i]) begin
            data_out = bank_data_out[i];
            valid_out = 1'b1;
        end
    end
end

endmodule