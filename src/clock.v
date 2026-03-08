/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// clock output for 24 MHz

module tt_um_hoene_clock (
    input       [4:0] divider,     // divider input
    input             nreset_in,   // nreset_in
    input  wire       ena,         // always 1 when the design is powered, so you can ignore it
    output reg        nreset_out,  // delayed high
    output reg        clock        // output clock signal
);
  wire clock_high;
  reg [4:0] counter;
  reg [9:0] reset_counter;

  // Ring of 27 inverters, output on should be 504MHz?
  ring_osc #(
      .DEPTH(27)
  ) ring_27 (
      .ena(ena),
      .osc_out(clock_high)
  );

  always @(posedge clock_high) begin
    counter <= counter + 1;
    if (counter == divider) begin
      clock <= ~clock;
      counter <= 0;
    end

    if (nreset_in == 0) begin
      reset_counter <= 0;
      nreset_out <= 0;
    end else if (reset_counter == 10'h3ff) begin
      nreset_out <= 1;
    end else begin
      reset_counter <= reset_counter + 1;
    end
  end

endmodule
