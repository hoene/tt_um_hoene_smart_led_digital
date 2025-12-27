/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hoene_mux (
    input  wire clk,     // Dedicated inputs
    input  wire data,    // Dedicated inputs
    input  wire reset_n, 
    input  wire exclusive,// Dedicated inputs
    output wire out0,    // Dedicated outputs
    output wire out1,    // Dedicated outputs
    output wire out2,    // Dedicated outputs
    output wire testmode,// Dedicated outputs
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule
