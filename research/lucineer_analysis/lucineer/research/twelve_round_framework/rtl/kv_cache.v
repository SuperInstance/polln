// ============================================================================
// KV Cache Module
// ============================================================================
// 32KB Key-Value Cache: 256 entries x 128 bytes
// Features:
// - 128-bit data path
// - Circular buffer implementation
// - Power-gated memory banks
// - 2-cycle read latency
// - Target: 28nm technology @ 1GHz
// ============================================================================

module kv_cache_32kb (
    // Clock and Reset
    input  wire         clk,            // 1GHz system clock
    input  wire         rst_n,          // Active-low asynchronous reset
    
    // Control signals
    input  wire         enable,         // Module enable
    input  wire         sleep,          // Sleep mode for power gating
    
    // Write Interface
    input  wire         wr_en,          // Write enable
    input  wire [7:0]   wr_addr,        // Write address (0-255)
    input  wire [127:0] wr_data,        // Write data (128-bit)
    
    // Read Interface
    input  wire         rd_en,          // Read enable
    input  wire [7:0]   rd_addr,        // Read address (0-255)
    output reg  [127:0] rd_data,        // Read data (2-cycle latency)
    output reg          rd_valid,       // Read data valid
    
    // Power Control
    output wire [3:0]   bank_pg_en_n,   // Active-low power gate enables for banks
    output reg          retention_en    // Retention mode enable
);

// ============================================================================
// Parameters and Local Parameters
// ============================================================================
parameter NUM_ENTRIES    = 256;         // 256 cache entries
parameter ENTRY_WIDTH    = 128;         // 128 bits per entry
parameter NUM_BANKS      = 4;           // 4 power-gated banks
parameter ENTRIES_PER_BANK = NUM_ENTRIES / NUM_BANKS; // 64 entries per bank

// Timing constraints for 1GHz operation (28nm technology)
// T_clk = 1ns, setup/hold margins included
// Max combinational path: 0.8ns (80% of clock period)
// Clock-to-Q: 0.15ns typical
// Memory access: 0.6ns worst-case

// ============================================================================
// Internal Signals
// ============================================================================
reg [ENTRY_WIDTH-1:0]   memory [0:NUM_ENTRIES-1];  // Main memory array
reg [7:0]               head_ptr;                  // Circular buffer head pointer
reg [7:0]               tail_ptr;                  // Circular buffer tail pointer
reg [7:0]               rd_addr_reg;               // Registered read address
reg                     rd_en_reg;                  // Registered read enable
reg [3:0]               bank_active;               // Bank activity indicator
reg [31:0]              access_counter;            // Access counter for power management

// Bank addressing
wire [1:0]              wr_bank_sel;               // Write bank select
wire [1:0]              rd_bank_sel;               // Read bank select
wire [5:0]              wr_bank_addr;              // Write address within bank
wire [5:0]              rd_bank_addr;              // Read address within bank

// Power gating control signals
reg [3:0]               bank_pg_state;             // Power gate state per bank
reg [3:0]               wakeup_counter;            // Wakeup counter for banks

// ============================================================================
// Circular Buffer Pointer Management
// ============================================================================
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        head_ptr <= 8'h00;
        tail_ptr <= 8'h00;
    end else if (enable) begin
        // Update head pointer on write
        if (wr_en) begin
            head_ptr <= head_ptr + 1'b1;
        end
        
        // Update tail pointer (example: on some eviction condition)
        // This is application-specific and should be customized
        if (wr_en && (head_ptr == tail_ptr)) begin
            tail_ptr <= tail_ptr + 1'b1;
        end
    end
end

// ============================================================================
// Bank Addressing Logic
// ============================================================================
// Bank selection: Divide 256 entries into 4 banks of 64 entries each
assign wr_bank_sel = wr_addr[7:6];      // Upper 2 bits select bank
assign rd_bank_sel = rd_addr[7:6];      // Upper 2 bits select bank
assign wr_bank_addr = wr_addr[5:0];     // Lower 6 bits for bank address
assign rd_bank_addr = rd_addr[5:0];     // Lower 6 bits for bank address

// ============================================================================
// Memory Write Operation
// ============================================================================
// Timing constraint: Memory write path must complete within 0.8ns
// This includes address decoding and memory cell access
always @(posedge clk) begin
    if (enable && wr_en) begin
        // Activate the bank being written to
        bank_active[wr_bank_sel] <= 1'b1;
        access_counter <= access_counter + 1'b1;
        
        // Write to memory
        memory[wr_addr] <= wr_data;
        
        // Power optimization: Update power gate state
        if (bank_pg_state[wr_bank_sel] == 1'b1) begin
            // Bank was powered down, initiate wakeup
            wakeup_counter[wr_bank_sel] <= 4'hF;  // 16-cycle wakeup
            bank_pg_state[wr_bank_sel] <= 1'b0;   // Mark as waking up
        end
    end
end

// ============================================================================
// Memory Read Operation (2-cycle latency)
// ============================================================================
// Stage 1: Address registration and bank activation
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        rd_addr_reg <= 8'h00;
        rd_en_reg <= 1'b0;
        rd_valid <= 1'b0;
    end else if (enable) begin
        rd_addr_reg <= rd_addr;
        rd_en_reg <= rd_en;
        rd_valid <= rd_en_reg;  // Valid on second cycle
        
        // Activate bank on read request
        if (rd_en) begin
            bank_active[rd_bank_sel] <= 1'b1;
            access_counter <= access_counter + 1'b1;
            
            // Power optimization: Handle bank wakeup
            if (bank_pg_state[rd_bank_sel] == 1'b1) begin
                wakeup_counter[rd_bank_sel] <= 4'hF;
                bank_pg_state[rd_bank_sel] <= 1'b0;
            end
        end
    end
end

// Stage 2: Data read and output registration
// Timing constraint: Memory read + mux must be < 0.8ns
always @(posedge clk) begin
    if (enable && rd_en_reg) begin
        // Read from memory with registered address
        rd_data <= memory[rd_addr_reg];
    end else if (!rd_en_reg) begin
        rd_data <= {ENTRY_WIDTH{1'b0}};
    end
end

// ============================================================================
// Power Gating Control
// ============================================================================
// Power optimization hints for 28nm:
// 1. Use header switches for power gating
// 2. Implement state retention for powered-down banks
// 3. Use isolation cells for outputs of powered-down banks
// 4. Implement wakeup/sleep sequencing

// Bank inactivity timer and power gating control
genvar i;
generate
    for (i = 0; i < NUM_BANKS; i = i + 1) begin : bank_power_ctrl
        reg [7:0] inactivity_timer;
        
        always @(posedge clk or negedge rst_n) begin
            if (!rst_n) begin
                inactivity_timer <= 8'hFF;
                bank_pg_state[i] <= 1'b0;  // 0=active, 1=power-gated
                wakeup_counter[i] <= 4'h0;
            end else if (enable && !sleep) begin
                // Decrement inactivity timer when bank is not active
                if (!bank_active[i] && inactivity_timer > 0) begin
                    inactivity_timer <= inactivity_timer - 1'b1;
                end
                
                // Reset timer when bank is accessed
                if (bank_active[i]) begin
                    inactivity_timer <= 8'hFF;
                end
                
                // Power gate bank after inactivity period
                if (inactivity_timer == 0 && wakeup_counter[i] == 0) begin
                    bank_pg_state[i] <= 1'b1;  // Power gate the bank
                end
                
                // Handle wakeup counter
                if (wakeup_counter[i] > 0) begin
                    wakeup_counter[i] <= wakeup_counter[i] - 1'b1;
                    if (wakeup_counter[i] == 1) begin
                        bank_pg_state[i] <= 1'b0;  // Bank is now active
                    end
                end
                
                // Clear bank active flag
                bank_active[i] <= 1'b0;
            end else if (sleep) begin
                // Sleep mode: power gate all banks
                bank_pg_state[i] <= 1'b1;
                inactivity_timer <= 8'hFF;
                wakeup_counter[i] <= 4'h0;
            end
        end
        
        // Power gate enable (active-low)
        assign bank_pg_en_n[i] = ~bank_pg_state[i];
    end
endgenerate

// Retention mode control
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        retention_en <= 1'b0;
    end else if (sleep) begin
        // Enable retention in sleep mode if any bank has data
        retention_en <= (head_ptr != tail_ptr);
    end else begin
        retention_en <= 1'b0;
    end
end

// ============================================================================
// Timing Constraints (SDC format comments)
// ============================================================================
/*
# Clock definition
create_clock -name clk -period 1.0 [get_ports clk]

# Input delays (assuming 30% of clock period for external logic)
set_input_delay -clock clk 0.3 [get_ports {wr_en wr_addr wr_data rd_en rd_addr}]
set_input_delay -clock clk 0.3 [get_ports {enable sleep}]

# Output delays
set_output_delay -clock clk 0.3 [get_ports {rd_data rd_valid bank_pg_en_n retention_en}]

# False paths
set_false_path -from [get_ports sleep] -to [get_ports bank_pg_en_n]

# Multicycle paths (for 2-cycle read)
set_multicycle_path -setup 2 -from [get_ports rd_addr] -to [get_ports rd_data]
set_multicycle_path -hold 1 -from [get_ports rd_addr] -to [get_ports rd_data]

# Memory timing
set_max_delay 0.8 -from [get_cells {memory[*]}] -to [get_cells rd_data_reg]

# Power gating timing
set_max_delay 0.5 -from [get_cells bank_pg_state[*]] -to [get_ports bank_pg_en_n[*]]
*/

// ============================================================================
// Power Optimization Directives
// ============================================================================
/*
# 28nm Power Optimization Hints:
# 1. Use multi-Vt libraries: HVT for memory arrays, LVT for critical paths
# 2. Implement clock gating for inactive banks
# 3. Use power-aware synthesis with UPF/CPF
# 4. Add level shifters between power domains
# 5. Use retention flip-flops for bank state registers
# 6. Implement dynamic voltage frequency scaling (DVFS) hooks
# 7. Use memory compiler with power-gating support
*/

// ============================================================================
// Simulation Initialization (Synthesis-safe)
// ============================================================================
// Note: In real design, memory initialization would be done via scan or BIST
// This is only for simulation
`ifdef SIMULATION
integer k;
initial begin
    for (k = 0; k < NUM_ENTRIES; k = k + 1) begin
        memory[k] = {ENTRY_WIDTH{1'b0}};
    end
    head_ptr = 8'h00;
    tail_ptr = 8'h00;
    rd_valid = 1'b0;
    rd_data = {ENTRY_WIDTH{1'b0}};
end
`endif

endmodule

// ============================================================================
// Optional: Clock Gating Cell Instantiation Template
// ============================================================================
/*
module clock_gater (
    input  wire clk,
    input  wire enable,
    input  wire test_mode,
    output wire gated_clk
);

// Integrated clock gating cell for 28nm
// CGCELLX4_28HPC for high drive strength
// Use library-specific implementation

endmodule
*/

// ============================================================================
// Module: kv_cache_32kb
// ============================================================================
// Summary:
// - 256 entries x 128 bits = 32KB storage
// - Circular buffer with head/tail pointers
// - 4 power-gated banks with inactivity timeout
// - 2-cycle read latency with registered outputs
// - Sleep mode with data retention support
// - 28nm-optimized with timing and power constraints
// ============================================================================