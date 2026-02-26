/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_hoene_smart_led_digital (
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
  //  assign uo_out[7] = 0;
  assign uio_out[6]  = 0;
  assign uio_oe[6:0] = 1;

  // List all unused inputs to prevent warnings
  wire _unused = &{uo_out, uio_out, uio_oe, ena, clk, rst_n, 1'b0};

  // wire up the signals of input_selector

  wire input_selector_in0;
  assign input_selector_in0 = ui_in[0];
  wire input_selector_in1;
  assign input_selector_in1 = ui_in[1];
  wire counters_test_mode;

  wire input_selector_out;
  assign uo_out[0] = input_selector_out;
  wire input_selector_in0selected;
  assign uo_out[1] = input_selector_in0selected;

  tt_um_hoene_input_selector all_input_selector (
      .in0        (input_selector_in0),
      .in1        (input_selector_in1),
      .testmode   (counters_test_mode),
      .clk        (clk),                        // clock
      .rst_n      (rst_n),                      // not reset
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
  wire framing_out_frame;
  wire framing_out_clk;
  wire framing_out_data;

  tt_um_hoene_framing user_framing (
      .in_data  (manchester_decoder_out_clk),
      .in_clk   (manchester_decoder_out_clk),
      .in_error (manchester_decoder_out_error),
      .rst_n    (rst_n),
      .clk      (clk),
      .out_frame(framing_out_frame),
      .out_data (framing_out_data),
      .out_clk  (framing_out_clk)
  );

  // wire up the signals of protocol counters module
  wire [4:0] counters_bits;
  wire counters_out_clk;
  wire counters_out_data;
  wire counters_test_mode_out;
  assign uo_out[6] = counters_test_mode_out;

  tt_um_hoene_protocol_counters user_protocol_counters (
      .in_clk     (framing_out_clk),
      .in_data    (framing_out_data),
      .in_frame   (framing_out_frame),
      .clk        (clk),
      .bit_counter(counters_bits),
      .test_mode  (counters_test_mode_out),
      .out_data   (counters_out_data),
      .out_clk    (counters_out_clk)
  );

  // wire up the signals of LED select module
  wire protocol_pwm_set; // the LED data shall be set if 1 and frame is falling, otherwise the LED data is not updated
  wire protocol_out_data;  // forward data to s2p and manachester encoder
  wire protocol_out_clk;  // forward clock to manachester encoder
  wire protocol_out_led_clk;  // forward clock to s2p
  wire protocol_error;  // error detected
  wire [1:0] protocol_state;  // 0->1->[2->]->3->0

  tt_um_hoene_protocol user_protocol (
      .in_data    (counters_out_data),
      .in_clk     (counters_out_clk),
      .in_frame   (framing_out_frame),
      .rst_n      (rst_n),
      .clk        (clk),
      .in0selected(input_selector_in0selected),
      .bit_counter(counters_bits),
      .pwm_set    (protocol_pwm_set),
      .out_data   (protocol_out_data),
      .out_clk    (protocol_out_clk),
      .out_led_clk(protocol_out_led_clk),
      .error      (protocol_error),
      .state      (protocol_state)
  );

  // wire up the signals of serial2parallel module
  wire [31:0] protocol_output_data;

  tt_um_hoene_protocol_serial2parallel user_protocol_serial2parallel (
      .in_data    (counters_out_data),
      .in_clk     (counters_out_clk),
      .store      (protocol_pwm_set && !framing_out_frame),
      .rst_n      (rst_n),
      .clk        (clk),
      .output_data(protocol_output_data)
  );

  // wire up the signals of pulse width modulator
  wire led_red;
  wire led_green;
  wire led_blue;

  tt_um_hoene_led_pwm user_led_pwm (
      .data_red  (protocol_output_data[10:1]),
      .data_green(protocol_output_data[20:11]),
      .data_blue (protocol_output_data[30:21]),
      .rst_n     (rst_n),
      .clk       (clk),
      .out_red   (led_red),
      .out_green (led_green),
      .out_blue  (led_blue)
  );

  // wire up the signals of pulse width modulator
  wire dout_data;
  wire dout_enable;
  assign uio_out[7] = dout_data;
  assign uio_oe[7]  = dout_enable;

  tt_um_hoene_manchester_encoder user_manchester_encoder (
      .in_data      (manchester_decoder_out_data),
      .in_clk       (manchester_decoder_out_clk),
      .in_error     (manchester_decoder_out_error),
      .in_pulsewidth(manchester_decoder_out_pulsewidth),
      .rst_n        (rst_n),
      .clk          (clk),
      .out_data     (dout_data),
      .out_enable   (dout_enable)
  );

endmodule
