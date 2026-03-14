// ============================================================================
// Processing Element (PE) with RAU, Activation Register, Partial Sum Register
// Weight-Stationary Dataflow with N/S/E/W Neighbor Connections
// Target: 28nm Technology @ 1GHz
// ============================================================================
// Features:
// - Weight-stationary dataflow: weights remain stationary in PE
// - RAU (Reduced Arithmetic Unit): 8-bit multiply-accumulate
// - Activation register with neighbor bypass
// - Partial sum accumulation with neighbor chaining
// - Sleep mode for power gating
// - Quad-directional neighbor interfaces (North/South/East/West)
// ============================================================================

`timescale 1ns / 1ps

module processing_element #(
    // =========================================================================
    // PARAMETERS
    // =========================================================================
    parameter DATA_WIDTH     = 8,     // Activation/weight data width
    parameter ACC_WIDTH      = 32,    // Accumulator width (prevents overflow)
    parameter PSUM_WIDTH     = 32,    // Partial sum width
    parameter WEIGHT_DEPTH   = 4      // Number of weights stored per PE
) (
    // =========================================================================
    // CLOCK, RESET, AND POWER CONTROL
    // =========================================================================
    input  wire                     clk,            // 1GHz system clock
    input  wire                     rst_n,          // Active-low synchronous reset
    input  wire                     sleep_en,       // Sleep mode enable (active high)
    
    // =========================================================================
    // DATA INPUTS/OUTPUTS
    // =========================================================================
    input  wire [DATA_WIDTH-1:0]    act_in,         // Activation input
    input  wire [DATA_WIDTH-1:0]    weight_in,      // Weight input (for loading)
    input  wire                     weight_load_en, // Weight load enable
    input  wire [1:0]               weight_addr,    // Weight memory address
    
    // =========================================================================
    // NEIGHBOR CONNECTIONS (N/S/E/W)
    // =========================================================================
    // North interface
    input  wire [DATA_WIDTH-1:0]    act_north_in,   // Activation from north neighbor
    input  wire [PSUM_WIDTH-1:0]    psum_north_in,  // Partial sum from north neighbor
    output wire [DATA_WIDTH-1:0]    act_north_out,  // Activation to north neighbor
    output wire [PSUM_WIDTH-1:0]    psum_north_out, // Partial sum to north neighbor
    
    // South interface
    input  wire [DATA_WIDTH-1:0]    act_south_in,   // Activation from south neighbor
    input  wire [PSUM_WIDTH-1:0]    psum_south_in,  // Partial sum from south neighbor
    output wire [DATA_WIDTH-1:0]    act_south_out,  // Activation to south neighbor
    output wire [PSUM_WIDTH-1:0]    psum_south_out, // Partial sum to south neighbor
    
    // East interface
    input  wire [DATA_WIDTH-1:0]    act_east_in,    // Activation from east neighbor
    input  wire [PSUM_WIDTH-1:0]    psum_east_in,   // Partial sum from east neighbor
    output wire [DATA_WIDTH-1:0]    act_east_out,   // Activation to east neighbor
    output wire [PSUM_WIDTH-1:0]    psum_east_out,  // Partial sum to east neighbor
    
    // West interface
    input  wire [DATA_WIDTH-1:0]    act_west_in,    // Activation from west neighbor
    input  wire [PSUM_WIDTH-1:0]    psum_west_in,   // Partial sum from west neighbor
    output wire [DATA_WIDTH-1:0]    act_west_out,   // Activation to west neighbor
    output wire [PSUM_WIDTH-1:0]    psum_west_out,  // Partial sum to west neighbor
    
    // =========================================================================
    // CONTROL SIGNALS
    // =========================================================================
    input  wire                     act_load_en,    // Activation load enable
    input  wire                     psum_clear,     // Clear partial sum register
    input  wire                     psum_acc_en,    // Enable partial sum accumulation
    input  wire [1:0]               act_dir_sel,    // Activation direction select
    input  wire [1:0]               psum_dir_sel,   // Partial sum direction select
    
    // =========================================================================
    // OUTPUTS
    // =========================================================================
    output wire [PSUM_WIDTH-1:0]    psum_out,       // Local partial sum output
    output wire                     psum_valid      // Partial sum valid flag
);

    // =========================================================================
    // TIMING CONSTRAINTS (for 28nm @ 1GHz = 1ns period)
    // =========================================================================
    // create_clock -name clk -period 1.0 [get_ports clk]
    // set_clock_uncertainty -setup 0.05 [get_clocks clk]
    // set_clock_uncertainty -hold 0.02 [get_clocks clk]
    // set_input_delay -clock clk -max 0.3 [get_ports act_in weight_in weight_load_en weight_addr act_load_en psum_clear psum_acc_en act_dir_sel psum_dir_sel sleep_en]
    // set_input_delay -clock clk -min 0.1 [get_ports act_in weight_in weight_load_en weight_addr act_load_en psum_clear psum_acc_en act_dir_sel psum_dir_sel sleep_en]
    // set_output_delay -clock clk -max 0.3 [get_ports act_north_out psum_north_out act_south_out psum_south_out act_east_out psum_east_out act_west_out psum_west_out psum_out psum_valid]
    // set_output_delay -clock clk -min 0.1 [get_ports act_north_out psum_north_out act_south_out psum_south_out act_east_out psum_east_out act_west_out psum_west_out psum_out psum_valid]
    // set_false_path -from [get_ports rst_n]
    // set_multicycle_path -setup 2 -from [get_cells weight_mem*] -to [get_cells rau_mult_result]
    
    // =========================================================================
    // POWER OPTIMIZATION HINTS
    // =========================================================================
    // 1. Use clock gating for sleep mode (implemented via enable registers)
    // 2. Multi-bit flops for data paths to reduce clock power
    // 3. Operand isolation on RAU when not in use
    // 4. Memory splitting for weight storage to reduce switching power
    // 5. Directional muxes use one-hot encoding for minimal switching
    
    // =========================================================================
    // INTERNAL SIGNALS
    // =========================================================================
    reg  [DATA_WIDTH-1:0]    activation_reg;        // Local activation register
    reg  [DATA_WIDTH-1:0]    weight_mem [0:WEIGHT_DEPTH-1]; // Weight storage
    reg  [PSUM_WIDTH-1:0]    partial_sum_reg;       // Partial sum accumulator
    wire [DATA_WIDTH-1:0]    selected_activation;   // Mux-selected activation
    wire [DATA_WIDTH-1:0]    selected_weight;       // Selected weight from memory
    wire [ACC_WIDTH-1:0]     rau_mult_result;       // RAU multiplication result
    wire [PSUM_WIDTH-1:0]    rau_output;            // RAU output after truncation
    wire [PSUM_WIDTH-1:0]    psum_to_accumulate;    // Selected psum for accumulation
    wire [PSUM_WIDTH-1:0]    next_partial_sum;      // Next partial sum value
    wire                     computation_en;        // Gated computation enable
    
    // =========================================================================
    // SLEEP MODE LOGIC (Clock Gating Enable)
    // =========================================================================
    // Power optimization: gate computation when in sleep mode
    assign computation_en = ~sleep_en;
    
    // =========================================================================
    // WEIGHT MEMORY (Weight-Stationary Storage)
    // =========================================================================
    // Weight-stationary: weights remain in PE across multiple computations
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all weights to zero
            for (integer i = 0; i < WEIGHT_DEPTH; i = i + 1) begin
                weight_mem[i] <= {DATA_WIDTH{1'b0}};
            end
        end else if (computation_en && weight_load_en) begin
            // Load weight into selected address
            weight_mem[weight_addr] <= weight_in;
        end
    end
    
    // Weight read (combinational)
    assign selected_weight = weight_mem[weight_addr];
    
    // =========================================================================
    // ACTIVATION REGISTER WITH NEIGHBOR BYPASS
    // =========================================================================
    // Mux for activation input selection
    reg [DATA_WIDTH-1:0] selected_activation_mux;
    always @(*) begin
        case (act_dir_sel)
            2'b00: selected_activation_mux = act_in;        // Local input
            2'b01: selected_activation_mux = act_north_in;  // From north
            2'b10: selected_activation_mux = act_south_in;  // From south
            2'b11: selected_activation_mux = act_east_in;   // From east
            // Note: west is not selectable as input to avoid redundancy
        endcase
    end
    assign selected_activation = selected_activation_mux;
    
    // Activation register with load enable
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            activation_reg <= {DATA_WIDTH{1'b0}};
        end else if (computation_en && act_load_en) begin
            activation_reg <= selected_activation;
        end
    end
    
    // =========================================================================
    // NEIGHBOR ACTIVATION OUTPUTS
    // =========================================================================
    // Broadcast local activation to all neighbors
    assign act_north_out = activation_reg;
    assign act_south_out = activation_reg;
    assign act_east_out  = activation_reg;
    assign act_west_out  = activation_reg;
    
    // =========================================================================
    // RAU (REDUCED ARITHMETIC UNIT)
    // =========================================================================
    // 8-bit signed multiplication with 32-bit accumulation
    // Power optimization: operand isolation using computation_en
    
    // Signed multiplication
    wire signed [DATA_WIDTH:0] signed_activation;
    wire signed [DATA_WIDTH:0] signed_weight;
    wire signed [2*DATA_WIDTH+1:0] signed_mult_result;
    
    assign signed_activation = {activation_reg[DATA_WIDTH-1], activation_reg};
    assign signed_weight = {selected_weight[DATA_WIDTH-1], selected_weight};
    assign signed_mult_result = signed_activation * signed_weight;
    
    // Truncate to ACC_WIDTH with saturation logic
    reg [ACC_WIDTH-1:0] mult_result_trunc;
    always @(*) begin
        if (computation_en) begin
            // Check for overflow
            if (signed_mult_result > (2**(ACC_WIDTH-1)-1)) begin
                mult_result_trunc = 2**(ACC_WIDTH-1)-1; // Positive saturation
            end else if (signed_mult_result < -(2**(ACC_WIDTH-1))) begin
                mult_result_trunc = {1'b1, {(ACC_WIDTH-1){1'b0}}}; // Negative saturation
            end else begin
                mult_result_trunc = signed_mult_result[ACC_WIDTH-1:0];
            end
        end else begin
            mult_result_trunc = {ACC_WIDTH{1'b0}}; // Operand isolation
        end
    end
    
    assign rau_mult_result = mult_result_trunc;
    
    // Truncate to PSUM_WIDTH for output
    assign rau_output = rau_mult_result[PSUM_WIDTH-1:0];
    
    // =========================================================================
    // PARTIAL SUM ACCUMULATION WITH NEIGHBOR CHAINING
    // =========================================================================
    // Mux for partial sum input selection (neighbor chaining)
    reg [PSUM_WIDTH-1:0] psum_input_mux;
    always @(*) begin
        case (psum_dir_sel)
            2'b00: psum_input_mux = rau_output;      // Local RAU output
            2'b01: psum_input_mux = psum_north_in;   // From north neighbor
            2'b10: psum_input_mux = psum_south_in;   // From south neighbor
            2'b11: psum_input_mux = psum_east_in;    // From east neighbor
        endcase
    end
    assign psum_to_accumulate = psum_input_mux;
    
    // Partial sum accumulation logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            partial_sum_reg <= {PSUM_WIDTH{1'b0}};
        end else if (computation_en) begin
            if (psum_clear) begin
                partial_sum_reg <= {PSUM_WIDTH{1'b0}};
            end else if (psum_acc_en) begin
                partial_sum_reg <= partial_sum_reg + psum_to_accumulate;
            end
        end
    end
    
    assign next_partial_sum = partial_sum_reg;
    
    // =========================================================================
    // NEIGHBOR PARTIAL SUM OUTPUTS
    // =========================================================================
    // Broadcast partial sum to all neighbors
    assign psum_north_out = next_partial_sum;
    assign psum_south_out = next_partial_sum;
    assign psum_east_out  = next_partial_sum;
    assign psum_west_out  = next_partial_sum;
    
    // =========================================================================
    // LOCAL OUTPUTS
    // =========================================================================
    assign psum_out = next_partial_sum;
    
    // Partial sum valid flag (set when accumulation is complete)
    reg psum_valid_reg;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            psum_valid_reg <= 1'b0;
        end else if (computation_en) begin
            // Valid when accumulation is enabled and not clearing
            psum_valid_reg <= psum_acc_en & ~psum_clear;
        end else begin
            psum_valid_reg <= 1'b0;
        end
    end
    assign psum_valid = psum_valid_reg;
    
    // =========================================================================
    // POWER GATING SUPPORT (for sleep mode)
    // =========================================================================
    // Note: In physical implementation, use:
    // - Isolation cells on outputs during sleep
    // - Retention flops for weight memory if needed
    // - Power switches controlled by sleep_en
    
    // =========================================================================
    // SYNTHESIS DIRECTIVES
    // =========================================================================
    // synthesis translate_off
    // Simulation-only code
    initial begin
        // Initialize weight memory for simulation
        for (integer i = 0; i < WEIGHT_DEPTH; i = i + 1) begin
            weight_mem[i] = {DATA_WIDTH{1'b0}};
        end
    end
    // synthesis translate_on
    
endmodule