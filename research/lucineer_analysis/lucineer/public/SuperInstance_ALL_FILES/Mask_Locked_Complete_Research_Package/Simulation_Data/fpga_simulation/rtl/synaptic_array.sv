//-----------------------------------------------------------------------------
// Module: synaptic_array
// Description: Array of RAUs implementing neural synaptic computation
//              Based on 20-30nm synaptic cleft geometry
//
// Biological Inspiration:
//   - Pre-zone (Active Zone): Input buffering
//   - Cleft (20-30nm): Weight encoding in metal
//   - Post-zone (PSD): Computation and accumulation
//
// Architecture: 256 parallel RAUs per tile
// Throughput: 52 GOPS per tile @ 800MHz (simulated)
//
// Author: SuperInstance.AI VP Manufacturing
// Version: 1.0
//-----------------------------------------------------------------------------

module synaptic_array #(
    parameter int NUM_RAUS = 256,
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24,
    parameter int WEIGHT_ENCODING = 2
)(
    input  logic                                  clk,
    input  logic                                  rst_n,
    
    // Activation input bus
    input  logic [NUM_RAUS-1:0][ACTIVATION_WIDTH-1:0] activations,
    input  logic                                      activations_valid,
    
    // Weight ROM interface (mask-locked weights)
    input  logic [NUM_RAUS-1:0][WEIGHT_ENCODING-1:0]  weights,
    
    // Control
    input  logic                                      accumulate_en,
    input  logic                                      clear_acc,
    
    // Partial sum output
    output logic signed [ACCUMULATOR_WIDTH-1:0]       partial_sum,
    output logic                                      result_valid
);

    //--------------------------------------------------------------------------
    // Internal signals
    //--------------------------------------------------------------------------
    
    // RAU array outputs
    logic signed [NUM_RAUS-1:0][ACCUMULATOR_WIDTH-1:0] rau_results;
    logic [NUM_RAUS-1:0] rau_valids;
    
    // Aggregated result
    logic signed [ACCUMULATOR_WIDTH+$clog2(NUM_RAUS):0] sum_accumulator;
    logic result_valid_d1, result_valid_d2;
    
    //--------------------------------------------------------------------------
    // RAU Array instantiation
    //--------------------------------------------------------------------------
    
    generate
        for (genvar i = 0; i < NUM_RAUS; i++) begin : gen_rau_array
            rau #(
                .ACTIVATION_WIDTH(ACTIVATION_WIDTH),
                .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH),
                .WEIGHT_ENCODING(WEIGHT_ENCODING)
            ) u_rau (
                .clk               (clk),
                .rst_n             (rst_n),
                .activation        (activations[i]),
                .activation_signed ($signed(activations[i])),
                .weight            (weights[i]),
                .valid_in          (activations_valid),
                .accumulate_en     (accumulate_en),
                .clear_acc         (clear_acc),
                .result            (rau_results[i]),
                .valid_out         (rau_valids[i])
            );
        end
    endgenerate

    //--------------------------------------------------------------------------
    // Population Count (Tree Adder for Partial Sum Aggregation)
    //--------------------------------------------------------------------------
    
    // Tree adder for efficient sum computation
    // 256 inputs -> 128 -> 64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1
    
    localparam int STAGES = $clog2(NUM_RAUS);
    localparam int SUM_WIDTH = ACCUMULATOR_WIDTH + STAGES;
    
    logic signed [SUM_WIDTH-1:0] adder_tree [STAGES+1][NUM_RAUS];
    
    // Initialize first stage with RAU results (sign-extended)
    always_comb begin
        for (int i = 0; i < NUM_RAUS; i++) begin
            adder_tree[0][i] = {{(SUM_WIDTH-ACCUMULATOR_WIDTH){rau_results[i][ACCUMULATOR_WIDTH-1]}}, rau_results[i]};
        end
    end
    
    // Tree reduction
    generate
        for (genvar stage = 0; stage < STAGES; stage++) begin : gen_adder_stage
            localparam int INPUTS_AT_STAGE = NUM_RAUS >> stage;
            localparam int OUTPUTS_AT_STAGE = INPUTS_AT_STAGE >> 1;
            
            for (genvar j = 0; j < OUTPUTS_AT_STAGE; j++) begin : gen_adders
                always_comb begin
                    adder_tree[stage+1][j] = adder_tree[stage][2*j] + adder_tree[stage][2*j+1];
                end
            end
        end
    endgenerate

    //--------------------------------------------------------------------------
    // Output registration
    //--------------------------------------------------------------------------
    
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            partial_sum <= '0;
            result_valid <= 1'b0;
        end else begin
            // Pipeline the result
            partial_sum <= adder_tree[STAGES][0][ACCUMULATOR_WIDTH-1:0];
            result_valid <= rau_valids[0];  // All RAUs should have same valid
        end
    end

    //--------------------------------------------------------------------------
    // Performance counters (for simulation/debug)
    //--------------------------------------------------------------------------
    
    `ifdef DEBUG
        int cycle_count;
        int operation_count;
        
        always_ff @(posedge clk or negedge rst_n) begin
            if (!rst_n) begin
                cycle_count <= 0;
                operation_count <= 0;
            end else begin
                cycle_count <= cycle_count + 1;
                if (activations_valid && accumulate_en) begin
                    operation_count <= operation_count + NUM_RAUS;
                end
            end
        end
    `endif

endmodule
