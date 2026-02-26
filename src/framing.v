/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// detect the frame start and end.

module tt_um_hoene_framing (
    input in_data,   // input data
    input in_clk,    // input clock
    input in_error,  // input error
    input rst_n,     // device reset
    input clk,       // global clock

    output reg out_frame,  // bitstream is insync and data is in the frame
    output reg out_data,  // the data delayed by one
    output reg out_clk  // the clock delayed by one
);
  always @(posedge clk) begin

    if (!rst_n) begin
      out_frame <= 0;
      out_data  <= 0;
      out_clk   <= 0;
    end else begin
      out_clk <= in_clk;
      if (in_error) begin
        out_frame <= 0;
      end
      if (in_clk) begin
        out_data <= in_data;
      end
      if (in_clk && !in_error && out_frame == 0 && out_data == 1 && in_data == 1) begin
        out_frame <= 1;
      end
    end
  end
endmodule
