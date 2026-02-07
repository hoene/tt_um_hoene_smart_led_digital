/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

function [5:0] realto6(input integer integer_value);
  if (integer_value[31:6] !== 0) begin
    $display("ASSERTION FAILED in %m");
    $finish;
  end
  realto6 = integer_value[5:0];
endfunction

// a manchester decoder for a given frequency

module tt_um_hoene_manchester_decoder #(
    parameter BIT_LENGTH = 24
) (
    input            in,             // first input 
    input            rst_n,          // device reset
    input            clk,            // global clock
    output reg       out_data,       // output signal
    output reg       out_clk,        // output clock
    output reg       out_error,      // error detected
    output reg [5:0] out_pulsewidth  // pulse width detected
);

  reg [5:0] counter;

  reg last_in;
  reg middle;

  always @(posedge clk) begin
    last_in <= in;  // always needed, e.g. for the first edge detection after reset
    if (!rst_n) begin
      counter <= 0;
      out_data <= 0;
      out_clk <= 0;
      out_error <= 1;  // we are not synchronized yet. Thus, we must remain in error state
      middle <= 0;
      out_pulsewidth <= BIT_LENGTH;
    end else if (last_in ^ in) begin
      if (counter >= realto6(BIT_LENGTH * 0.75) && counter < realto6(BIT_LENGTH * 1.5)) begin
        out_data <= last_in;  // we have a long impulse, always data out
        out_clk <= 1;
        out_error <= 0;
        middle <= 1;
        out_pulsewidth <= counter;
        counter <= 0;
      end else if (counter >= realto6(
              BIT_LENGTH * 0.25
          ) && counter < realto6(
              BIT_LENGTH * 0.75
          ) && !out_error) begin
        if (!middle) begin
          // second half of short pulse
          out_data <= last_in;  // data out
          out_clk  <= 1;
          counter  <= 0;
        end else begin
          // first half of short pulse
          out_data <= 0;
          out_clk  <= 0;
          counter  <= 0;
        end
        middle <= ~middle;
      end else begin
        // invalid pulse length
        out_data  <= 0;
        out_clk   <= 0;
        out_error <= 1;
        counter   <= 0;
      end
    end else begin  // no change in the signal. continue to measure its pulse length
      counter  <= counter + 1;
      out_data <= 0;
      out_clk  <= 0;
    end
  end

endmodule
