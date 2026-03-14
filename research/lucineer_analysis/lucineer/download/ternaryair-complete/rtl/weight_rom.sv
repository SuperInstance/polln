/**
 * Weight ROM - Mask-Locked Weight Storage
 * 
 * Ternary weights encoded as via patterns in metal layers.
 * This is the "mask-locked" part of TernaryAir.
 * 
 * In actual silicon:
 * - Via present between Metal1 and Metal2 = weight +1
 * - Via to complement rail = weight -1
 * - No via = weight 0
 * 
 * Author: Casey DiGennaro / SuperInstance.AI
 * License: MIT
 */

module weight_rom #(
    parameter int NUM_WEIGHTS  = 768,     // Number of weights per row
    parameter int WEIGHT_WIDTH = 2,       // 2-bit ternary encoding
    parameter string WEIGHT_FILE = "weights.hex"  // Weight initialization file
)(
    input  logic [$clog2(NUM_WEIGHTS)-1:0] addr,
    output logic [WEIGHT_WIDTH-1:0]        weight
);

    // Weight encoding:
    // 2'b00 = +1
    // 2'b01 = 0
    // 2'b10 = -1
    // 2'b11 = reserved
    
    // In actual silicon, these would be hardwired via patterns
    // For simulation/FPGA, we use a ROM initialized from file
    
    logic [WEIGHT_WIDTH-1:0] rom [NUM_WEIGHTS];
    
    // Initialize from hex file (for simulation)
    initial begin
        $readmemh(WEIGHT_FILE, rom);
    end
    
    // Asynchronous read (combinatorial in actual silicon)
    always_comb begin
        weight = rom[addr];
    end
    
    // Synthesis directive for FPGA implementation
    // In actual ASIC, this entire block is replaced with
    // direct metal routing patterns
    
`ifdef FPGA_SYNTHESIS
    // FPGA implementation uses distributed ROM
    (* rom_style = "distributed" *)
`endif

endmodule
