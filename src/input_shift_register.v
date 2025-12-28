/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hoene_shift_in_with_parity (
    input in_data,            // input bit to a 32bit shift register. The format is 30 bits data, 1 bit use flag, 1 bit parity
    input in_clock,  // clock signal to shift in the bits positive edge
    input rst_n,  // active low reset signal
    input clk,  // global clock signal
    output reg [31:0] output_data  // the output data of the shift register
);

  reg last_in_clock;
  reg parity;

  always @(posedge clk or rst_n) begin
    if (!rst_n) begin
      parity <= 1'b0;
    end else begin
      output_data <= output_data >> 1;
      output_data[31] <= in_data;
      parity <= parity ^ in_data;
    end
  end

endmodule
