/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hoene_serial2parallel (
    input in_data,  // input bit to a 30bit shift register.
    input in_clk,  // clock signal to shift in the bits positive edge
    input store,  // store the data to the output signals
    input rst_n,  // active low reset signal
    input clk,  // global clock signal

    output reg [29:0] output_data  // the output data of the shift register
);
  reg [29:0] shift_register;  // the output data of the shift register

  always @(posedge clk) begin
    if (!rst_n) begin
      output_data <= 0;
      shift_register <= 0;
    end else begin
      if (in_clk) begin
        shift_register <= shift_register >> 1;
        shift_register[29] <= in_data;
      end
      if (store) begin
        output_data <= shift_register;
      end
    end
  end

endmodule
