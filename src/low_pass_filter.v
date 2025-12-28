/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// a 3 bit low pass filter

module tt_um_hoene_low_pass_filter (
    input      in,     // first input 
    input      rst_n,  // device reset
    input      clk,    // global clock
    output reg out     // output signal
);

  reg last1;
  reg last0;

  always @(posedge clk) begin
    if (!rst_n) begin
      last1 <= 0;
      last0 <= 0;
      out   <= 0;
    end else begin
      last1 <= last0;
      last0 <= in;
      out   <= (in & (last0 | last1)) | (last0 & last1);  // at least two bits high to make out
    end
  end

endmodule
