// Mask-locked weight ROM
// 512 ternary weights packed 4 per byte
// Metal-layer programmable at manufacturing
// Zero standby power (ROM not SRAM)
// Row/column redundancy for yield
// Single-cycle read

// Define the ROM size
`define ROM_SIZE 512
`define WORD_SIZE 4
`define ADDRESS_WIDTH $clog2(`ROM_SIZE)

// Define the ternary weight type
typedef enum logic [1:0] {
  ZERO,
  ONE,
  NEG_ONE
} ternary_weight_t;

// Define the ROM array type
typedef ternary_weight_t [0:`WORD_SIZE-1] rom_word_t;
typedef rom_word_t [0:`ROM_SIZE-1] rom_array_t;

// Define the ROM module
module mask_locked_weight_rom(
  input  logic [`ADDRESS_WIDTH-1:0] address,
  output logic [2*`WORD_SIZE-1:0] data
);

  // Define the ROM array
  rom_array_t rom_array;

  // Initialize the ROM array with ternary weights
  // This will be replaced with metal-layer programming at manufacturing
  initial begin
    for (int i = 0; i < `ROM_SIZE; i++) begin
      for (int j = 0; j < `WORD_SIZE; j++) begin
        // Replace with actual ternary weights
        rom_array[i][j] = ZERO;
      end
    end
  end

  // Define the read logic
  always_comb begin
    // Single-cycle read
    data = {rom_array[address][3], rom_array[address][2], rom_array[address][1], rom_array[address][0]};
  end

  // Timing constraints
  // set_input_delay -clock clock 0.0 address;
  // set_output_delay -clock clock 0.0 data;

  // Power optimization hints
  // set_power_optimization -mode area;
  // set_power_optimization -mode leakage;

endmodule