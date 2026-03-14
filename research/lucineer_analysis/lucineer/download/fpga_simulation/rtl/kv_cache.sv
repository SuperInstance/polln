//-----------------------------------------------------------------------------
// Module: kv_cache_controller
// Description: Hierarchical KV cache with spine-like distributed storage
//
// Biological Inspiration: Dendritic spine working memory
//   - Active cache: Spine heads (fast, transient)
//   - Spill cache: Spine necks (medium latency)
//   - Backing cache: Dendritic trunk (slow, large)
//
// Memory Organization for BitNet 2B:
//   - Layers: 24
//   - Heads: 16 per layer
//   - Head dimension: 64
//   - KV per token: 2 × 16 × 64 = 2048 elements
//   - Element size: 8-bit quantized
//   - KV size per token: 2KB
//
// Total: 16MB for 4096 token context
//
// Author: VP Manufacturing, SuperInstance.AI
// Version: 1.0
//-----------------------------------------------------------------------------

module kv_cache_controller #(
    parameter int NUM_LAYERS = 24,
    parameter int NUM_HEADS = 16,
    parameter int HEAD_DIM = 64,
    parameter int MAX_SEQ_LEN = 4096,
    parameter int ACTIVATION_WIDTH = 8,
    
    // Derived parameters
    parameter int KV_PER_TOKEN = 2 * NUM_HEADS * HEAD_DIM,  // K and V
    parameter int BYTES_PER_TOKEN = KV_PER_TOKEN,  // 8-bit = 1 byte each
    parameter int CACHE_SIZE_BYTES = MAX_SEQ_LEN * BYTES_PER_TOKEN * NUM_LAYERS
)(
    input  logic clk,
    input  logic rst_n,
    
    //--------------------------------------------------------------------------
    // Write Interface (KV update during inference)
    //--------------------------------------------------------------------------
    
    input  logic                         kv_write_en,
    input  logic [$clog2(NUM_LAYERS)-1:0] layer_select_wr,
    input  logic [$clog2(NUM_HEADS)-1:0]  head_select_wr,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] position_wr,
    input  logic [KV_PER_TOKEN*ACTIVATION_WIDTH-1:0] kv_data_in,
    output logic                         kv_write_done,
    
    //--------------------------------------------------------------------------
    // Read Interface (KV access during attention)
    //--------------------------------------------------------------------------
    
    input  logic                         kv_read_en,
    input  logic [$clog2(NUM_LAYERS)-1:0] layer_select_rd,
    input  logic [$clog2(NUM_HEADS)-1:0]  head_select_rd,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] position_rd_start,
    input  logic [$clog2(MAX_SEQ_LEN)-1:0] position_rd_end,
    output logic [KV_PER_TOKEN*ACTIVATION_WIDTH-1:0] kv_data_out,
    output logic                         kv_read_done,
    output logic                         kv_stream_valid,
    
    //--------------------------------------------------------------------------
    // Status
    //--------------------------------------------------------------------------
    
    output logic [$clog2(MAX_SEQ_LEN)-1:0] current_seq_len,
    output logic                         cache_full
);

    //--------------------------------------------------------------------------
    // Memory Type Definitions
    //--------------------------------------------------------------------------
    
    // Hierarchical cache structure (mimics biological spine organization)
    // Level 0: Active cache (SRAM, fast) - tokens 0-127
    // Level 1: Spill cache (SRAM, medium) - tokens 128-511
    // Level 2: Backing cache (eDRAM/external) - tokens 512+
    
    localparam int LEVEL0_TOKENS = 128;
    localparam int LEVEL1_TOKENS = 384;  // 128-511
    localparam int LEVEL2_TOKENS = MAX_SEQ_LEN - 512;
    
    //--------------------------------------------------------------------------
    // Address Calculation
    //--------------------------------------------------------------------------
    
    function automatic [31:0] calc_address;
        input int layer, head, position;
        
        // Address = (layer * MAX_SEQ_LEN + position) * KV_PER_TOKEN + head * HEAD_DIM
        calc_address = (layer * MAX_SEQ_LEN + position) * KV_PER_TOKEN + head * HEAD_DIM;
    endfunction
    
    //--------------------------------------------------------------------------
    // Active Cache (Level 0) - 128 tokens × 24 layers × 2KB = 6MB SRAM
    // This is the hottest data - recently generated tokens
    //--------------------------------------------------------------------------
    
    localparam int LEVEL0_SIZE = LEVEL0_TOKENS * BYTES_PER_TOKEN * NUM_LAYERS;
    
    logic [ACTIVATION_WIDTH-1:0] level0_cache [0:LEVEL0_SIZE-1];
    
    // SRAM interface signals
    logic [31:0] level0_addr;
    logic level0_wr_en;
    logic level0_rd_en;
    logic [63:0] level0_wr_data;
    logic [63:0] level0_rd_data;
    
    //--------------------------------------------------------------------------
    // Spill Cache (Level 1) - 384 tokens × 24 layers × 2KB = 18MB SRAM
    //--------------------------------------------------------------------------
    
    localparam int LEVEL1_SIZE = LEVEL1_TOKENS * BYTES_PER_TOKEN * NUM_LAYERS;
    
    logic [ACTIVATION_WIDTH-1:0] level1_cache [0:LEVEL1_SIZE-1];
    
    //--------------------------------------------------------------------------
    // Backing Cache (Level 2) - External memory interface
    //--------------------------------------------------------------------------
    
    // External memory interface signals (to LPDDR4 or similar)
    logic [31:0] ext_mem_addr;
    logic ext_mem_rd_en;
    logic ext_mem_wr_en;
    logic [63:0] ext_mem_data;
    logic ext_mem_valid;
    
    //--------------------------------------------------------------------------
    // Cache Access State Machine
    //--------------------------------------------------------------------------
    
    typedef enum logic [2:0] {
        IDLE,
        WRITE_LEVEL0,
        WRITE_LEVEL1,
        WRITE_LEVEL2,
        READ_LEVEL0,
        READ_LEVEL1,
        READ_LEVEL2,
        STREAM_OUTPUT
    } state_t;
    
    state_t current_state, next_state;
    
    // State machine
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            current_state <= IDLE;
            current_seq_len <= 0;
        end else begin
            current_state <= next_state;
            
            // Update sequence length on write
            if (kv_write_en && position_wr >= current_seq_len) begin
                current_seq_len <= position_wr + 1;
            end
        end
    end
    
    // State transitions
    always_comb begin
        next_state = current_state;
        
        case (current_state)
            IDLE: begin
                if (kv_write_en)
                    next_state = (position_wr < LEVEL0_TOKENS) ? WRITE_LEVEL0 :
                                 (position_wr < 512) ? WRITE_LEVEL1 : WRITE_LEVEL2;
                else if (kv_read_en)
                    next_state = (position_rd_start < LEVEL0_TOKENS) ? READ_LEVEL0 :
                                 (position_rd_start < 512) ? READ_LEVEL1 : READ_LEVEL2;
            end
            
            WRITE_LEVEL0, WRITE_LEVEL1, WRITE_LEVEL2: begin
                next_state = IDLE;
            end
            
            READ_LEVEL0, READ_LEVEL1, READ_LEVEL2: begin
                next_state = STREAM_OUTPUT;
            end
            
            STREAM_OUTPUT: begin
                // Stream output until all positions read
                if (/* streaming complete */ 1'b0)
                    next_state = IDLE;
            end
            
            default: next_state = IDLE;
        endcase
    end
    
    //--------------------------------------------------------------------------
    // Level 0 Cache Access
    //--------------------------------------------------------------------------
    
    always_ff @(posedge clk) begin
        if (level0_wr_en && current_state == WRITE_LEVEL0) begin
            // Write 64-bit chunks
            for (int i = 0; i < 8; i++) begin
                level0_cache[level0_addr + i] <= level0_wr_data[i*8 +: 8];
            end
        end
    end
    
    always_comb begin
        level0_rd_data = '0;
        for (int i = 0; i < 8; i++) begin
            level0_rd_data[i*8 +: 8] = level0_cache[level0_addr + i];
        end
    end
    
    //--------------------------------------------------------------------------
    // Performance Monitoring
    //--------------------------------------------------------------------------
    
    `ifdef DEBUG
        int level0_hits;
        int level1_hits;
        int level2_hits;
        int total_accesses;
        
        always_ff @(posedge clk) begin
            if (kv_read_en) begin
                total_accesses <= total_accesses + 1;
                
                if (position_rd_start < LEVEL0_TOKENS)
                    level0_hits <= level0_hits + 1;
                else if (position_rd_start < 512)
                    level1_hits <= level1_hits + 1;
                else
                    level2_hits <= level2_hits + 1;
            end
        end
    `endif
    
    //--------------------------------------------------------------------------
    // Cache Full Detection
    //--------------------------------------------------------------------------
    
    assign cache_full = (current_seq_len >= MAX_SEQ_LEN - 1);
    
    //--------------------------------------------------------------------------
    // Assertions
    //--------------------------------------------------------------------------
    
    `ifdef FORMAL
        // Position should never exceed max
        always @(posedge clk) begin
            if (kv_write_en) begin
                assert (position_wr < MAX_SEQ_LEN) else
                    $error("Position exceeds maximum sequence length");
            end
        end
    `endif

endmodule
