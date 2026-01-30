/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hoene_firsttry (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
  assign uo_out[7] = 0;
  assign uio_out[7:6] = 0;
  assign uio_oe = 1;

  // List all unused inputs to prevent warnings
  wire _unused = &{uo_out, uio_out, uio_oe, ena, clk, rst_n, 1'b0};



  // wire up the signals of input_selector

  wire input_selector_in0;
  assign input_selector_in0 = ui_in[0];
  wire input_selector_in1;
  assign input_selector_in1 = ui_in[1];
  wire protocol_counters_test_mode;
  assign protocol_counters_test_mode = ui_in[2];

  wire input_selector_out;
  assign uo_out[0] = input_selector_out;
  wire input_selector_in0selected;
  assign uo_out[1] = input_selector_in0selected;

  tt_um_hoene_input_selector all_input_selector (
      .in0        (input_selector_in0),
      .in1        (input_selector_in1),
      .testmode   (protocol_counters_test_mode),
      .clk        (clk),                          // clock
      .rst_n      (rst_n),                        // not reset
      .out        (input_selector_out),
      .in0selected(input_selector_in0selected)
  );

  // wire up the signals of low pass filter
  wire low_pass_filter_out;
  assign uo_out[2] = low_pass_filter_out;

  tt_um_hoene_low_pass_filter all_low_pass_filter (
      .in   (input_selector_out),
      .clk  (clk),                 // clock
      .rst_n(rst_n),               // not reset
      .out  (low_pass_filter_out)
  );

  // wire up the signals of Manchester decoder
  wire manchester_decoder_out_data;
  assign uo_out[3] = manchester_decoder_out_data;
  wire manchester_decoder_out_clk;
  assign uo_out[4] = manchester_decoder_out_clk;
  wire manchester_decoder_out_error;
  assign uo_out[5] = manchester_decoder_out_error;
  wire [5:0] manchester_decoder_out_pulsewidth;
  assign uio_out[5:0] = manchester_decoder_out_pulsewidth;

  tt_um_hoene_manchester_decoder user_manchester_decoder (
      .in            (low_pass_filter_out),
      .clk           (clk),                               // clock
      .rst_n         (rst_n),                             // not reset
      .out_data      (manchester_decoder_out_data),
      .out_clk       (manchester_decoder_out_clk),
      .out_error     (manchester_decoder_out_error),
      .out_pulsewidth(manchester_decoder_out_pulsewidth)
  );


  // wire up the signals of protocol insync module
  wire protocol_insync_out;
  wire protocol_insync_out_clk;
  wire protocol_insync_out_data;

  tt_um_hoene_protocol_insync user_protocol_insync (
      .in_data (manchester_decoder_out_clk),
      .in_clk  (manchester_decoder_out_clk),
      .in_error(manchester_decoder_out_error),
      .rst_n   (rst_n),
      .clk     (clk),
      .insync  (protocol_insync_out),
      .out_data(protocol_insync_out_data),
      .out_clk (protocol_insync_out_clk)
  );



  // wire up the signals of protocol counters module
  wire [4:0] protocol_counters_bits;
  wire protocol_counters_out_clk;
  wire protocol_counters_out_data;
  wire protocol_counters_test_mode_out;
  assign uo_out[6] = protocol_counters_test_mode_out;

  tt_um_hoene_protocol_counters user_protocol_counters (
      .in_clk     (protocol_insync_out_clk),
      .in_data    (protocol_insync_out_data),
      .in_sync    (protocol_insync_out),
      .clk        (clk),
      .bit_counter(protocol_counters_bits),
      .test_mode  (protocol_counters_test_mode_out),
      .out_data   (protocol_counters_out_data),
      .out_clk    (protocol_counters_out_clk)
  );
endmodule
