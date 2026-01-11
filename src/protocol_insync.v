/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// a 3 bit low pass filter

module tt_um_hoene_protocol_insync (
    input in_data,   // input data
    input in_clk,    // input clock
    input in_error,  // input error
    input rst_n,     // device reset
    input clk,       // global clock

    output reg insync  // bitstream is insync
);
  reg last_in;

  always @(posedge clk) begin


    if (!rst_n || in_error) begin
      insync  <= 0;
      last_in <= 0;
    end else if (in_clk) begin
      last_in <= in_data;

      // check for init state
      if (!insync) begin  // the first byte is 10101011b
        if (last_in == 1 && in_data == 1) begin
          insync <= 1;
        end
      end
    end
  end
endmodule
