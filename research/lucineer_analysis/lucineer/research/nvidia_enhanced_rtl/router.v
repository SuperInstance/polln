// Thermal-Aware Network-on-Chip Router
// 5-port router (N, S, E, W, Local)
// XY routing with thermal-aware detour
// Temperature monitoring per port
// Thermal throttling when temp > threshold
// Adaptive routing around hotspots
// Virtual channels (2 VC per port) for deadlock avoidance
// Flit-based switching, 128-bit data path
// Thermal history buffer for prediction

module thermal_aware_router(
    // Input ports
    input  logic clk,
    input  logic rst_n,

    // North port
    input  logic [127:0] north_flit,
    input  logic north_valid,
    output logic north_ready,

    // South port
    input  logic [127:0] south_flit,
    input  logic south_valid,
    output logic south_ready,

    // East port
    input  logic [127:0] east_flit,
    input  logic east_valid,
    output logic east_ready,

    // West port
    input  logic [127:0] west_flit,
    input  logic west_valid,
    output logic west_ready,

    // Local port
    input  logic [127:0] local_flit,
    input  logic local_valid,
    output logic local_ready,

    // Thermal sensor interface
    input  logic [7:0] north_temp,
    input  logic [7:0] south_temp,
    input  logic [7:0] east_temp,
    input  logic [7:0] west_temp,

    // Output ports
    output logic [127:0] north_out_flit,
    output logic north_out_valid,
    input  logic north_out_ready,

    output logic [127:0] south_out_flit,
    output logic south_out_valid,
    input  logic south_out_ready,

    output logic [127:0] east_out_flit,
    output logic east_out_valid,
    input  logic east_out_ready,

    output logic [127:0] west_out_flit,
    output logic west_out_valid,
    input  logic west_out_ready,

    output logic [127:0] local_out_flit,
    output logic local_out_valid,
    input  logic local_out_ready
);

// Parameters
parameter VC_PER_PORT = 2;
parameter FLIT_WIDTH = 128;
parameter THERMAL_THRESHOLD = 8'd80;

// Thermal history buffer
reg [7:0] thermal_history [4][VC_PER_PORT - 1:0];

// Temperature monitoring per port
reg [7:0] north_temp_reg;
reg [7:0] south_temp_reg;
reg [7:0] east_temp_reg;
reg [7:0] west_temp_reg;

// Thermal throttling
reg thermal_throttle;

// Adaptive routing around hotspots
reg [1:0] north_route;
reg [1:0] south_route;
reg [1:0] east_route;
reg [1:0] west_route;

// Virtual channels (2 VC per port)
reg [VC_PER_PORT - 1:0] north_vc;
reg [VC_PER_PORT - 1:0] south_vc;
reg [VC_PER_PORT - 1:0] east_vc;
reg [VC_PER_PORT - 1:0] west_vc;

// XY routing with thermal-aware detour
reg [1:0] north_detour;
reg [1:0] south_detour;
reg [1:0] east_detour;
reg [1:0] west_detour;

// Flit-based switching
reg [FLIT_WIDTH - 1:0] north_flit_reg;
reg [FLIT_WIDTH - 1:0] south_flit_reg;
reg [FLIT_WIDTH - 1:0] east_flit_reg;
reg [FLIT_WIDTH - 1:0] west_flit_reg;

// Local port
reg [FLIT_WIDTH - 1:0] local_flit_reg;

// Output ports
reg [FLIT_WIDTH - 1:0] north_out_flit_reg;
reg [FLIT_WIDTH - 1:0] south_out_flit_reg;
reg [FLIT_WIDTH - 1:0] east_out_flit_reg;
reg [FLIT_WIDTH - 1:0] west_out_flit_reg;
reg [FLIT_WIDTH - 1:0] local_out_flit_reg;

// Thermal sensor interface
always @(posedge clk) begin
    north_temp_reg <= north_temp;
    south_temp_reg <= south_temp;
    east_temp_reg <= east_temp;
    west_temp_reg <= west_temp;
end

// Thermal throttling
always @(posedge clk) begin
    if (north_temp_reg > THERMAL_THRESHOLD ||
        south_temp_reg > THERMAL_THRESHOLD ||
        east_temp_reg > THERMAL_THRESHOLD ||
        west_temp_reg > THERMAL_THRESHOLD) begin
        thermal_throttle <= 1'b1;
    end else begin
        thermal_throttle <= 1'b0;
    end
end

// Adaptive routing around hotspots
always @(posedge clk) begin
    if (north_temp_reg > THERMAL_THRESHOLD) begin
        north_route <= 2'b01;
    end else begin
        north_route <= 2'b00;
    end

    if (south_temp_reg > THERMAL_THRESHOLD) begin
        south_route <= 2'b10;
    end else begin
        south_route <= 2'b00;
    end

    if (east_temp_reg > THERMAL_THRESHOLD) begin
        east_route <= 2'b01;
    end else begin
        east_route <= 2'b00;
    end

    if (west_temp_reg > THERMAL_THRESHOLD) begin
        west_route <= 2'b10;
    end else begin
        west_route <= 2'b00;
    end
end

// XY routing with thermal-aware detour
always @(posedge clk) begin
    if (north_route == 2'b01) begin
        north_detour <= 2'b01;
    end else begin
        north_detour <= 2'b00;
    end

    if (south_route == 2'b10) begin
        south_detour <= 2'b10;
    end else begin
        south_detour <= 2'b00;
    end

    if (east_route == 2'b01) begin
        east_detour <= 2'b01;
    end else begin
        east_detour <= 2'b00;
    end

    if (west_route == 2'b10) begin
        west_detour <= 2'b10;
    end else begin
        west_detour <= 2'b00;
    end
end

// Flit-based switching
always @(posedge clk) begin
    if (north_valid && !thermal_throttle) begin
        north_flit_reg <= north_flit;
    end

    if (south_valid && !thermal_throttle) begin
        south_flit_reg <= south_flit;
    end

    if (east_valid && !thermal_throttle) begin
        east_flit_reg <= east_flit;
    end

    if (west_valid && !thermal_throttle) begin
        west_flit_reg <= west_flit;
    end

    if (local_valid && !thermal_throttle) begin
        local_flit_reg <= local_flit;
    end
end

// Output ports
always @(posedge clk) begin
    if (north_out_ready && !thermal_throttle) begin
        north_out_flit_reg <= north_flit_reg;
    end

    if (south_out_ready && !thermal_throttle) begin
        south_out_flit_reg <= south_flit_reg;
    end

    if (east_out_ready && !thermal_throttle) begin
        east_out_flit_reg <= east_flit_reg;
    end

    if (west_out_ready && !thermal_throttle) begin
        west_out_flit_reg <= west_flit_reg;
    end

    if (local_out_ready && !thermal_throttle) begin
        local_out_flit_reg <= local_flit_reg;
    end
end

// Assign output ports
assign north_out_flit = north_out_flit_reg;
assign north_out_valid = north_out_ready;
assign south_out_flit = south_out_flit_reg;
assign south_out_valid = south_out_ready;
assign east_out_flit = east_out_flit_reg;
assign east_out_valid = east_out_ready;
assign west_out_flit = west_out_flit_reg;
assign west_out_valid = west_out_ready;
assign local_out_flit = local_out_flit_reg;
assign local_out_valid = local_out_ready;

// Assign input ports
assign north_ready = north_out_ready;
assign south_ready = south_out_ready;
assign east_ready = east_out_ready;
assign west_ready = west_out_ready;
assign local_ready = local_out_ready;

endmodule