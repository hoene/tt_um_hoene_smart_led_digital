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
  assign uo_out  = ui_in + uio_in;  // Example: ou_out is the sum of ui_in and uio_in
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};


  // ui0 input_selector_in0;
  // ui1 input_selector_in1;


  // wire up the signals of input_selector

  reg  input_selector_testmode;  // TODO
  wire input_selector_out;
  wire input_selector_in0selected;

  tt_um_hoene_input_selector all_input_selector (
      .in0        (ui_in[0]),
      .in1        (ui_in[1]),
      .testmode   (protocol_test_mode),
      .clk        (clk),                        // clock
      .rst_n      (rst_n),                      // not reset
      .out        (input_selector_out),
      .in0selected(input_selector_in0selected)
  );

  // wire up the signals of low pass filter
  wire low_pass_filter_out;

  tt_um_hoene_low_pass_filter all_low_pass_filter (
      .in   (input_selector_out),
      .clk  (clk),                 // clock
      .rst_n(rst_n),               // not reset
      .out  (low_pass_filter_out)
  );

  // wire up the signals of Manchester decoder
  wire manchester_decoder_out_data;
  wire manchester_decoder_out_clk;
  wire manchester_decoder_out_error;
  wire [5:0] manchester_decoder_out_pulsewidth;

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

  tt_um_hoene_protocol_insync user_protocol_insync (
      .in_data (manchester_decoder_out_clk),
      .in_clk  (manchester_decoder_out_clk),
      .in_error(manchester_decoder_out_error),
      .rst_n   (rst_n),
      .clk     (clk),
      .insync  (protocol_insync_out)
  );

  // wire up the signals of protocol insync module
  wire protocol_pwm_set;   // forwarded clock to manachester encoder
  wire protocol_swap_forward_bit; // swap the bit, which is forwarded
  wire protocol_test_mode;  // test mode is selected if too many LED data


  tt_um_hoene_protocol_select user_protocol_select (
      .in_data (manchester_decoder_out_data),
      .in_clk  (manchester_decoder_out_clk),
      .in_sync (protocol_insync_out),
      .rst_n   (rst_n),
      .clk     (clk),
      .in0selected  (input_selector_in0selected),
      .pwm_set (protocol_pwm_set),
      .swap_forward_bit (protocol_swap_forward_bit),
      .test_mode (protocol_test_mode)
  );

    wire  [31:0] protocol_data;  // the output data of the shift register

    tt_um_hoene_protocol_serial2parallel user_protocol_serial2parallel (
      .in_data (manchester_decoder_out_data),
      .in_clk  (manchester_decoder_out_clk),
      .store   (protocol_pwm_set),
      .rst_n   (rst_n),
      .clk     (clk),
      .output_data  (protocol_data)
  );

  // wire up the signals of led PWM 
  reg [9:0] led_pwm_data_red;
  reg [9:0] led_pwm_data_green;
  reg [9:0] led_pwm_data_blue;
  wire led_pwm_out_red;
  wire led_pwm_out_green;
  wire led_pwm_out_blue;

  tt_um_hoene_led_pwm user_led_pwm (
      .data_red  (led_pwm_data_red),
      .data_green(led_pwm_data_green),
      .data_blue (led_pwm_data_blue),
      .rst_n     (rst_n),
      .clk       (clk),
      .out_red   (led_pwm_out_red),
      .out_green (led_pwm_out_green),
      .out_blue  (led_pwm_out_blue)
  );



endmodule
