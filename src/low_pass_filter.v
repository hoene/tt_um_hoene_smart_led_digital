/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// a 5 bit low pass filter

module tt_um_hoene_low_pass_filter (
    input      in,     // first input 
    input      rst_n,  // device reset
    input      clk,    // global clock
    output reg out     // output signal
);
  reg last3;
  reg last2;
  reg last1;
  reg last0;

  always @(posedge clk) begin
    if (!rst_n) begin
      last3 <= 0;
      last2 <= 0;
      last1 <= 0;
      last0 <= 0;
      out   <= 0;
    end else begin
      last3 <= last2;
      last2 <= last1;
      last1 <= last0;
      last0 <= in;
      // add least three bits high to make out high, so that short spikes are filtered out, but the output is still responsive
      out <= (in & last0 & last1) | (in & last0 & last2) | (in & last0 & last3) |
          (in & last1 & last2) | (in & last1 & last3) |
          (in & last2 & last3) | (last0 & last1 & last2) |
          (last0 & last1 & last3) | (last0 & last2 & last3) |
          (last1 & last2 & last3);
    end
  end

endmodule
