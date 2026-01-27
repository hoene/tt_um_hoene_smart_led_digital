/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// selects input 0 or input 1 and forwards it to out depening on two conditions 
// 1) If input 0 receives bits, then input 0 is selected after 64 cycles, otherwise input 1 is taken.
// 2) Overwriting the decision of 1), if the test mode is selected, then the decision of 1) is swapped.

module tt_um_hoene_input_selector (
    input      in0,         // first input
    input      in1,         // second input
    input      rst_n,       // device reset
    input      clk,         // global clock
    input      testmode,    // high if the other input shall be chosen regardless
    output reg out,         // output signal
    output reg in0selected  //  high if in0 is selected, otherwise in1 is selected
);

  reg [5:0] counter;
  reg last_in0;

  always @(posedge clk) begin
    if (!rst_n) begin
      in0selected <= 0;
      last_in0 <= 0;
      counter <= 0;
      out <= 0;
    end else begin
      last_in0 <= in0;
      if (last_in0 == 0 && in0 == 1 && counter != 63) begin
        counter <= counter + 1;
      end
      if ((counter == 63 & !testmode) || (counter != 63 & testmode)) begin
        in0selected <= 1;
        out <= in0;
      end else begin
        in0selected <= 0;
        out <= in1;
      end
    end
  end

endmodule
