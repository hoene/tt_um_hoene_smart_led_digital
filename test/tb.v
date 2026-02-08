`default_nettype none `timescale 1ns / 1ps
`include "input_selector.v"
`include "low_pass_filter.v"
`include "manchester_decoder.v"
`include "led_pwm.v"
`include "protocol_insync.v"
`include "protocol_serial2parallel.v"
`include "protocol_counters.v"
`include "protocol_parity.v"
`include "protocol_select.v"
`include "manchester_encoder.v"

/* This testbench just instantiates the module and makes some convenient wires
   that can be driven / tested by the cocotb test.py.
*/
module tb ();

  // Dump the signals to a FST file. You can view it with gtkwave or surfer.
  initial begin
    $dumpfile("tb.fst");
    $dumpvars(0, tb);
    #1;
  end

  // Wire up the inputs and outputs:
  reg clk;
  reg rst_n;
  reg ena;
  reg [7:0] ui_in;
  reg [7:0] uio_in;
  wire [7:0] uo_out;
  wire [7:0] uio_out;
  wire [7:0] uio_oe;

  // Replace tt_um_example with your module name:
  tt_um_hoene_firsttry user_project (
      .ui_in  (ui_in),    // Dedicated inputs
      .uo_out (uo_out),   // Dedicated outputs
      .uio_in (uio_in),   // IOs: Input path
      .uio_out(uio_out),  // IOs: Output path
      .uio_oe (uio_oe),   // IOs: Enable path (active high: 0=input, 1=output)
      .ena    (ena),      // enable - goes high when design is selected
      .clk    (clk),      // clock
      .rst_n  (rst_n)     // not reset
  );

  // wire up the signals of input_selector
  reg  input_selector_in0;
  reg  input_selector_in1;
  reg  input_selector_testmode;
  wire input_selector_out;
  wire input_selector_in0selected;

  tt_um_hoene_input_selector user_input_selector (
      .in0        (input_selector_in0),
      .in1        (input_selector_in1),
      .testmode   (input_selector_testmode),
      .clk        (clk),                        // clock
      .rst_n      (rst_n),                      // not reset
      .out        (input_selector_out),
      .in0selected(input_selector_in0selected)
  );

  // wire up the signals of low pass filter
  reg  low_pass_filter_in;
  wire low_pass_filter_out;

  tt_um_hoene_low_pass_filter user_low_pass_filter (
      .in   (low_pass_filter_in),
      .clk  (clk),                 // clock
      .rst_n(rst_n),               // not reset
      .out  (low_pass_filter_out)
  );

  // wire up the signals of Manchester decoder
  reg manchester_decoder_in;
  wire manchester_decoder_out_data;
  wire manchester_decoder_out_clk;
  wire manchester_decoder_out_error;
  wire [5:0] manchester_decoder_out_pulsewidth;

  tt_um_hoene_manchester_decoder user_manchester_decoder (
      .in            (manchester_decoder_in),
      .clk           (clk),                               // clock
      .rst_n         (rst_n),                             // not reset
      .out_data      (manchester_decoder_out_data),
      .out_clk       (manchester_decoder_out_clk),
      .out_error     (manchester_decoder_out_error),
      .out_pulsewidth(manchester_decoder_out_pulsewidth)
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

  // wire up the signals of protocol insync module
  reg  protocol_insync_data;
  reg  protocol_insync_clk;
  reg  protocol_insync_error;
  wire protocol_insync_out;
  wire protocol_insync_out_data;
  wire protocol_insync_out_clk;

  tt_um_hoene_protocol_insync user_protocol_insync (
      .in_data (protocol_insync_data),
      .in_clk  (protocol_insync_clk),
      .in_error(protocol_insync_error),
      .rst_n   (rst_n),
      .clk     (clk),
      .insync  (protocol_insync_out),
      .out_data(protocol_insync_out_data),
      .out_clk (protocol_insync_out_clk)
  );

  // wire up the signals of protocol serial2parallel module
  reg protocol_serial2parallel_data;
  reg protocol_serial2parallel_clk;
  reg protocol_serial2parallel_store;
  wire [31:0] protocol_serial2parallel_out;

  tt_um_hoene_protocol_serial2parallel user_protocol_serial2parallel (
      .in_data    (protocol_serial2parallel_data),
      .in_clk     (protocol_serial2parallel_clk),
      .store      (protocol_serial2parallel_store),
      .rst_n      (rst_n),
      .clk        (clk),
      .output_data(protocol_serial2parallel_out)
  );

  // wire up the signals of protocol counters module
  reg protocol_counters_in_clk;
  reg protocol_counters_in_data;
  reg protocol_counters_in_sync;
  wire [4:0] protocol_counters_bits;
  wire protocol_counters_test_mode;
  wire protocol_counters_out_data;
  wire protocol_counters_out_clk;

  tt_um_hoene_protocol_counters user_protocol_counters (
      .in_clk     (protocol_counters_in_clk),
      .in_data    (protocol_counters_in_data),
      .in_sync    (protocol_counters_in_sync),
      .clk        (clk),
      .bit_counter(protocol_counters_bits),
      .test_mode  (protocol_counters_test_mode),
      .out_data   (protocol_counters_out_data),
      .out_clk    (protocol_counters_out_clk)
  );

  // wire up the signals of protocol parity module
  reg protocol_parity_in_data;
  reg protocol_parity_in_clk;
  reg protocol_parity_in_sync;
  reg [4:0] protocol_parity_bits;
  wire protocol_parity_error;

  tt_um_hoene_protocol_parity user_protocol_parity (
      .in_data    (protocol_parity_in_data),
      .in_clk     (protocol_parity_in_clk),
      .in_sync    (protocol_parity_in_sync),
      .clk        (clk),
      .bit_counter(protocol_parity_bits),
      .error      (protocol_parity_error)
  );

  // wire up the signals of protocol parity module
  reg protocol_select_in_data;
  reg protocol_select_in_clk;
  reg protocol_select_in_sync;
  reg protocol_select_in0selected;
  reg [4:0] protocol_select_bits;
  wire protocol_select_pwm_set;
  wire protocol_select_swap_forward_bit;
  wire protocol_select_error;
  wire [1:0] protocol_select_state;

  tt_um_hoene_protocol_select user_protocol_select (
      .in_data         (protocol_select_in_data),
      .in_clk          (protocol_select_in_clk),
      .in_sync         (protocol_select_in_sync),
      .in0selected     (protocol_select_in0selected),
      .bit_counter     (protocol_select_bits),
      .rst_n           (rst_n),
      .clk             (clk),
      .pwm_set         (protocol_select_pwm_set),
      .swap_forward_bit(protocol_select_swap_forward_bit),
      .error           (protocol_select_error),
      .state           (protocol_select_state)
  );

  // wire up the signals of Manchester decoder
  reg manchester_encoder_in_data;
  reg manchester_encoder_in_clk;
  reg manchester_encoder_in_error;
  reg [5:0] manchester_encoder_in_pulsewidth;
  wire manchester_encoder_out_data;
  wire manchester_encoder_out_enable;

  tt_um_hoene_manchester_encoder user_manchester_denoder (
      .in_data      (manchester_encoder_in_data),
      .in_clk       (manchester_encoder_in_clk),
      .in_error     (manchester_encoder_in_error),
      .in_pulsewidth(manchester_encoder_in_pulsewidth),
      .clk          (clk),                               // clock
      .rst_n        (rst_n),                             // not reset
      .out_enable   (manchester_encoder_out_enable),
      .out_data     (manchester_encoder_out_data)
  );


endmodule
