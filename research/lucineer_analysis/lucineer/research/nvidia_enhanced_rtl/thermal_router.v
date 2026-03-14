// Thermal-aware Router in Verilog
module thermal_router(
    // Input ports
    input  logic [127:0]  north_in_flit,
    input  logic         north_in_valid,
    output logic         north_in_ready,

    input  logic [127:0]  south_in_flit,
    input  logic         south_in_valid,
    output logic         south_in_ready,

    input  logic [127:0]  east_in_flit,
    input  logic         east_in_valid,
    output logic         east_in_ready,

    input  logic [127:0]  west_in_flit,
    input  logic         west_in_valid,
    output logic         west_in_ready,

    input  logic [127:0]  local_in_flit,
    input  logic         local_in_valid,
    output logic         local_in_ready,

    // Output ports
    output logic [127:0]  north_out_flit,
    output logic         north_out_valid,
    input  logic         north_out_ready,

    output logic [127:0]  south_out_flit,
    output logic         south_out_valid,
    input  logic         south_out_ready,

    output logic [127:0]  east_out_flit,
    output logic         east_out_valid,
    input  logic         east_out_ready,

    output logic [127:0]  west_out_flit,
    output logic         west_out_valid,
    input  logic         west_out_ready,

    output logic [127:0]  local_out_flit,
    output logic         local_out_valid,
    input  logic         local_out_ready,

    // Temperature input for throttling
    input  logic [31:0]   temperature,

    // Clock and reset
    input  logic         clk,
    input  logic         rst
);

// Virtual channel buffers
logic [127:0]  north_vc0_buffer [7:0];
logic [127:0]  north_vc1_buffer [7:0];
logic [127:0]  south_vc0_buffer [7:0];
logic [127:0]  south_vc1_buffer [7:0];
logic [127:0]  east_vc0_buffer [7:0];
logic [127:0]  east_vc1_buffer [7:0];
logic [127:0]  west_vc0_buffer [7:0];
logic [127:0]  west_vc1_buffer [7:0];
logic [127:0]  local_vc0_buffer [7:0];
logic [127:0]  local_vc1_buffer [7:0];

// XY routing with thermal detour
logic [1:0]  routing_decision;
logic        thermal_detour;

// Temperature-based throttling
logic        throttle;

// Routing logic
always_comb begin
    // XY routing
    if (north_in_valid && !north_vc0_buffer[0]) begin
        routing_decision = 2'b00; // North
    end else if (south_in_valid && !south_vc0_buffer[0]) begin
        routing_decision = 2'b01; // South
    end else if (east_in_valid && !east_vc0_buffer[0]) begin
        routing_decision = 2'b10; // East
    end else if (west_in_valid && !west_vc0_buffer[0]) begin
        routing_decision = 2'b11; // West
    end else begin
        routing_decision = 2'b00; // Default to North
    end

    // Thermal detour
    if (temperature > 32'd80) begin
        thermal_detour = 1'b1;
    end else begin
        thermal_detour = 1'b0;
    end

    // Temperature-based throttling
    if (temperature > 32'd90) begin
        throttle = 1'b1;
    end else begin
        throttle = 1'b0;
    end
end

// Virtual channel allocation
always_ff @(posedge clk) begin
    if (rst) begin
        // Reset virtual channel buffers
        for (int i = 0; i < 8; i++) begin
            north_vc0_buffer[i] <= 128'd0;
            north_vc1_buffer[i] <= 128'd0;
            south_vc0_buffer[i] <= 128'd0;
            south_vc1_buffer[i] <= 128'd0;
            east_vc0_buffer[i] <= 128'd0;
            east_vc1_buffer[i] <= 128'd0;
            west_vc0_buffer[i] <= 128'd0;
            west_vc1_buffer[i] <= 128'd0;
            local_vc0_buffer[i] <= 128'd0;
            local_vc1_buffer[i] <= 128'd0;
        end
    end else begin
        // Allocate virtual channels
        if (north_in_valid && !north_vc0_buffer[0]) begin
            north_vc0_buffer[0] <= north_in_flit;
        end else if (south_in_valid && !south_vc0_buffer[0]) begin
            south_vc0_buffer[0] <= south_in_flit;
        end else if (east_in_valid && !east_vc0_buffer[0]) begin
            east_vc0_buffer[0] <= east_in_flit;
        end else if (west_in_valid && !west_vc0_buffer[0]) begin
            west_vc0_buffer[0] <= west_in_flit;
        end else if (local_in_valid && !local_vc0_buffer[0]) begin
            local_vc0_buffer[0] <= local_in_flit;
        end
    end
end

// Output logic
always_comb begin
    // North output
    if (routing_decision == 2'b00 && !throttle) begin
        north_out_flit = north_vc0_buffer[0];
        north_out_valid = 1'b1;
    end else begin
        north_out_flit = 128'd0;
        north_out_valid = 1'b0;
    end

    // South output
    if (routing_decision == 2'b01 && !throttle) begin
        south_out_flit = south_vc0_buffer[0];
        south_out_valid = 1'b1;
    end else begin
        south_out_flit = 128'd0;
        south_out_valid = 1'b0;
    end

    // East output
    if (routing_decision == 2'b10 && !throttle) begin
        east_out_flit = east_vc0_buffer[0];
        east_out_valid = 1'b1;
    end else begin
        east_out_flit = 128'd0;
        east_out_valid = 1'b0;
    end

    // West output
    if (routing_decision == 2'b11 && !throttle) begin
        west_out_flit = west_vc0_buffer[0];
        west_out_valid = 1'b1;
    end else begin
        west_out_flit = 128'd0;
        west_out_valid = 1'b0;
    end

    // Local output
    if (routing_decision == 2'b00 && thermal_detour) begin
        local_out_flit = north_vc0_buffer[0];
        local_out_valid = 1'b1;
    end else begin
        local_out_flit = 128'd0;
        local_out_valid = 1'b0;
    end
end

// Input ready signals
always_comb begin
    north_in_ready = !north_vc0_buffer[0];
    south_in_ready = !south_vc0_buffer[0];
    east_in_ready = !east_vc0_buffer[0];
    west_in_ready = !west_vc0_buffer[0];
    local_in_ready = !local_vc0_buffer[0];
end

endmodule