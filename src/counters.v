/*
 * Copyright (c) 2026 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_protocol_counters (
    input            in_clk,       // input clock
    input            in_data,      // input data
    input            in_frame,     // input frame
    input            clk,          // global clock
    output reg [4:0] bit_counter,  // bit counter
    output reg       test_mode    // test mode is selected if too many LED data
);

  reg [11:0] led_counter;

  always @(posedge clk) begin

    if (!in_frame) begin
      // reset
      bit_counter <= 5'b0;
      led_counter <= 12'b0;
      test_mode <= 0;
    end else begin
      if (in_clk) begin
        // increase counters. If too many LEDs received, enter test mode      
        bit_counter <= bit_counter + 1;
        if (bit_counter == 31) begin
          bit_counter <= 5'b0;
          if (led_counter == 12'hFFF) begin
            test_mode <= 1;
          end else begin
            led_counter <= led_counter + 1;
          end
        end
      end
    end
  end
endmodule
