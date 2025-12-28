`default_nettype none `timescale 1ns / 1ps
`include "input_selector.v"
`include "input_shift_register.v"
`include "low_pass_filter.v"
`include "manchester_decoder.v"

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
  reg  manchester_decoder_in;
  wire manchester_decoder_out_data;
  wire manchester_decoder_out_clk;
  wire manchester_decoder_out_error;

  tt_um_hoene_manchester_decoder user_manchester_decoder (
      .in       (manchester_decoder_in),
      .clk      (clk),                          // clock
      .rst_n    (rst_n),                        // not reset
      .out_data (manchester_decoder_out_data),
      .out_clk  (manchester_decoder_out_clk),
      .out_error(manchester_decoder_out_error)
  );

endmodule
