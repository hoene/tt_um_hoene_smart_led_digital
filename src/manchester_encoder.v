/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_manchester_encoder (
    input            in_data,        // input data
    input            in_clk,         // input clock
    input            in_error,       // input is invalid
    input      [5:0] in_pulsewidth,  // pulse width of the input signal
    input            clk,            // global clock
    input            rst_n,          // device reset
    output reg       out_data,       // data output signal
    output reg       out_enable      // output enable signal for the data output
);

  reg [4:0] counter;
  reg middle;

  always @(posedge clk) begin
    // reset
    if (!rst_n || in_error) begin
      out_enable <= 0;
      out_data <= 0;
      counter <= 0;
      middle <= 1;
    end else if (in_clk) begin
      out_enable <= 1;
      out_data <= in_data;  // swap the bit, which is forwarded
      counter <= in_pulsewidth[5:1];  // divide by 2, because we want to forward the clock, which is half the frequency of the data
      middle <= 0;
    end else if (counter > 0) begin
      counter <= counter - 1;
    end else if (middle == 0) begin
      out_data <= ~out_data;
      counter  <= in_pulsewidth[5:1];
      middle   <= 1;
    end
  end
endmodule
