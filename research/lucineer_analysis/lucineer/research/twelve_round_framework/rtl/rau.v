// ============================================================================
// Rotation-Accumulate Unit for Ternary Neural Network Inference
// ============================================================================
// Target: 28nm technology @ 1GHz
// Features:
//   - 8-bit signed activation input
//   - 2-bit ternary weight encoding: 00=-1, 01=0, 10=+1
//   - 2-stage pipeline for high throughput
//   - Clock gating for power optimization
//   - Fully synthesizable (IEEE 1364-2005 compliant)
// ============================================================================

module rotation_accumulate_unit (
    // System Interface
    input  wire         clk,          // Main clock (1GHz)
    input  wire         clk_en,       // Clock enable for power gating
    input  wire         rst_n,        // Active-low synchronous reset
    
    // Data Interface
    input  wire [7:0]   activation,   // 8-bit signed activation [-128, 127]
    input  wire [1:0]   weight,       // 2-bit ternary weight encoding
    input  wire         valid_in,     // Input data valid
    
    // Control Interface
    input  wire         accum_clear,  // Clear accumulation register
    input  wire         accum_enable, // Enable accumulation
    
    // Output Interface
    output reg  [15:0]  accum_out,    // 16-bit accumulation result
    output reg          valid_out     // Output data valid
);

// ============================================================================
// Local Parameters and Signals
// ============================================================================

// Weight decoding constants
localparam [1:0] WEIGHT_MINUS = 2'b00;  // Weight = -1
localparam [1:0] WEIGHT_ZERO  = 2'b01;  // Weight = 0
localparam [1:0] WEIGHT_PLUS  = 2'b10;  // Weight = +1

// Pipeline stages
reg  [7:0]   act_reg;      // Stage 1: Registered activation
reg  [1:0]   weight_reg;   // Stage 1: Registered weight
reg          valid_reg;    // Stage 1: Registered valid

reg  [15:0]  mult_result;  // Stage 2: Multiplication result
reg  [15:0]  accum_reg;    // Accumulation register
reg          valid_dly;    // Stage 2: Delayed valid

// Clock gating signals
wire         gated_clk;    // Gated clock for power optimization

// ============================================================================
// Clock Gating Implementation
// ============================================================================
// Power Optimization Hint: Use integrated clock gating cell (ICG) in 28nm
// Synthesis tool will infer ICG from this structure
// Timing Constraint: Setup clk_en to clk rising edge (0.1ns margin @ 1GHz)
reg  clk_en_reg;
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        clk_en_reg <= 1'b0;
    end else begin
        clk_en_reg <= clk_en;
    end
end

assign gated_clk = clk & clk_en_reg;

// ============================================================================
// Pipeline Stage 1: Input Registration
// ============================================================================
// Timing Constraint: activation[7:0] -> act_reg[7:0] setup = 0.9ns @ 1GHz
// Timing Constraint: weight[1:0] -> weight_reg[1:0] setup = 0.9ns @ 1GHz
always @(posedge gated_clk or negedge rst_n) begin
    if (!rst_n) begin
        act_reg    <= 8'b0;
        weight_reg <= 2'b0;
        valid_reg  <= 1'b0;
    end else begin
        act_reg    <= activation;
        weight_reg <= weight;
        valid_reg  <= valid_in;
    end
end

// ============================================================================
// Pipeline Stage 2: Multiplication and Accumulation
// ============================================================================

// Ternary multiplication: activation * weight
// Power Optimization Hint: Use case statement for explicit weight decoding
// This enables better power gating of unused arithmetic paths
always @(*) begin
    case (weight_reg)
        WEIGHT_MINUS: begin
            // Multiply by -1: Two's complement negation
            mult_result = {{8{act_reg[7]}}, act_reg};  // Sign extend to 16-bit
            mult_result = ~mult_result + 1;            // Two's complement
        end
        
        WEIGHT_ZERO: begin
            // Multiply by 0
            mult_result = 16'b0;
        end
        
        WEIGHT_PLUS: begin
            // Multiply by +1: Direct assignment with sign extension
            mult_result = {{8{act_reg[7]}}, act_reg};
        end
        
        default: begin
            // Default case for synthesis completeness
            mult_result = 16'b0;
        end
    endcase
end

// Accumulation with clear/enable control
// Timing Constraint: mult_result[15:0] -> accum_reg[15:0] setup = 0.9ns @ 1GHz
// Power Optimization Hint: Use explicit enable conditions to prevent
// unnecessary switching activity in accum_reg
always @(posedge gated_clk or negedge rst_n) begin
    if (!rst_n) begin
        accum_reg <= 16'b0;
        valid_dly <= 1'b0;
    end else begin
        valid_dly <= valid_reg;
        
        if (accum_clear) begin
            accum_reg <= 16'b0;
        end else if (valid_reg && accum_enable) begin
            accum_reg <= accum_reg + mult_result;
        end
        // Else hold current value (implicit in reg behavior)
    end
end

// ============================================================================
// Output Assignment
// ============================================================================
// Timing Constraint: accum_reg[15:0] -> accum_out[15:0] setup = 0.9ns @ 1GHz
always @(posedge gated_clk or negedge rst_n) begin
    if (!rst_n) begin
        accum_out <= 16'b0;
        valid_out <= 1'b0;
    end else begin
        accum_out <= accum_reg;
        valid_out <= valid_dly;
    end
end

// ============================================================================
// Power Optimization Hints (as synthesis pragmas/comments)
// ============================================================================
// 1. Clock Gating: Already implemented with gated_clk
// 2. Operand Isolation: Case statement isolates unused arithmetic paths
// 3. Register Banking: Consider splitting accum_reg if timing critical
// 4. Multi-Vt Cells: Use HVT for accum_reg, SVT for pipeline, LVT for crit path
// 5. Power Gating: Consider adding power switches for sleep modes if needed

// ============================================================================
// Timing Constraints Summary (for SDC file)
// ============================================================================
/*
create_clock -name clk -period 1.0 [get_ports clk]
set_clock_gating_check -setup 0.05 -hold 0.05 [get_cells clk_en_reg]
set_input_delay -clock clk -max 0.9 [get_ports {activation[*] weight[*] valid_in accum_clear accum_enable}]
set_output_delay -clock clk -max 0.9 [get_ports {accum_out[*] valid_out}]
set_multicycle_path -setup 2 -from [get_pins valid_reg] -to [get_pins valid_out]
set_false_path -from [get_ports accum_clear] -to [get_ports accum_out]
*/

endmodule