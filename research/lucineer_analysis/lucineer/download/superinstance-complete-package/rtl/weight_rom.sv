/**
 * TernaryAir RTL Package
 * Weight ROM - Storage for Non-Ternary Parameters
 * 
 * MIT License - Open Source Hardware
 * Author: Casey DiGennaro
 * Repository: github.com/superinstance/ternaryair
 * 
 * While ternary weights {-1, 0, +1} are mask-locked into metal routing,
 * additional parameters require storage:
 *   - Layer normalization scale (gamma) and bias (beta)
 *   - Attention scaling factors
 *   - Output biases
 * 
 * This module provides parameterized ROM storage for these values.
 */

module weight_rom #(
    parameter int DEPTH = 4096,
    parameter int DATA_WIDTH = 16,  // FP16
    parameter string INIT_FILE = "" // Optional initialization file
)(
    input  logic                        clk,
    input  logic [$clog2(DEPTH)-1:0]    addr,
    output logic [DATA_WIDTH-1:0]       data
);

    // ROM storage
    (* rom_style = "block" *) logic [DATA_WIDTH-1:0] rom [DEPTH];
    
    // Initialize from file if provided
    initial begin
        if (INIT_FILE != "") begin
            $readmemh(INIT_FILE, rom);
        end else begin
            // Default: all zeros (will be overwritten during configuration)
            for (int i = 0; i < DEPTH; i++) begin
                rom[i] = '0;
            end
        end
    end
    
    // Synchronous read
    always_ff @(posedge clk) begin
        data <= rom[addr];
    end

endmodule

/**
 * Layer Parameter Bank
 * Stores normalization and scaling parameters for one layer
 */
module layer_param_bank #(
    parameter int HIDDEN_SIZE = 2048,
    parameter int NUM_HEADS = 16,
    parameter int DATA_WIDTH = 16
)(
    input  logic                        clk,
    input  logic                        rst_n,
    
    // Parameter selection
    input  logic                        select_layer_norm1,  // LayerNorm1 (attention output)
    input  logic                        select_layer_norm2,  // LayerNorm2 (FFN output)
    input  logic                        select_attn_scale,   // Attention scale (1/sqrt(d))
    
    // Index for gamma/beta
    input  logic [$clog2(HIDDEN_SIZE)-1:0] idx,
    
    // Output
    output logic [DATA_WIDTH-1:0]       param_out,
    output logic                        param_valid
);

    // Parameter storage (simplified - would be ROM in production)
    logic [DATA_WIDTH-1:0] ln1_gamma [HIDDEN_SIZE];
    logic [DATA_WIDTH-1:0] ln1_beta  [HIDDEN_SIZE];
    logic [DATA_WIDTH-1:0] ln2_gamma [HIDDEN_SIZE];
    logic [DATA_WIDTH-1:0] ln2_beta  [HIDDEN_SIZE];
    logic [DATA_WIDTH-1:0] attn_scale;
    
    // Initialize with default values
    initial begin
        // Gamma defaults to 1.0 (FP16 = 0x3C00)
        for (int i = 0; i < HIDDEN_SIZE; i++) begin
            ln1_gamma[i] = 16'h3C00;
            ln2_gamma[i] = 16'h3C00;
            ln1_beta[i] = '0;
            ln2_beta[i] = '0;
        end
        // Attention scale = 1/sqrt(HIDDEN_SIZE/NUM_HEADS) = 1/sqrt(128) ≈ 0.088
        attn_scale = 16'h2D40;  // FP16 approximation
    end
    
    // Read logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            param_out <= '0;
            param_valid <= 1'b0;
        end else begin
            param_valid <= 1'b1;
            
            if (select_layer_norm1) begin
                // Interleave gamma/beta based on MSB of address
                if (idx[$clog2(HIDDEN_SIZE)-1]) begin
                    param_out <= ln1_beta[idx];
                end else begin
                    param_out <= ln1_gamma[idx];
                end
            end else if (select_layer_norm2) begin
                if (idx[$clog2(HIDDEN_SIZE)-1]) begin
                    param_out <= ln2_beta[idx];
                end else begin
                    param_out <= ln2_gamma[idx];
                end
            end else if (select_attn_scale) begin
                param_out <= attn_scale;
            end else begin
                param_out <= '0;
                param_valid <= 1'b0;
            end
        end
    end

endmodule
