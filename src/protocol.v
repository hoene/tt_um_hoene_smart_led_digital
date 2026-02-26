/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_protocol (
    input            in_data,      // input data
    input            in_clk,       // input clock
    input            in_frame,     // input is valid
    input            clk,          // global clock
    input            rst_n,        // device reset
    input            in0selected,  // mode from input selector DIN or BIN
    input      [4:0] bit_counter,
    output reg       pwm_set,      // if 1 and frame is falling, set LED output
    output reg       out_data,     // output data
    output reg       out_clk,      // output clock for TX
    output reg       out_led_clk,  // output clock for LED data
    output reg       error,        // error detected
    output reg [1:0] state         // 0->1->[2->]->3->0
);
  reg parity;

  always @(posedge clk) begin
    // reset
    if (!rst_n || !in_frame) begin
      state <= 0;
      pwm_set <= 0;
      error <= 0;
      out_data <= in_data;
      out_clk <= in_clk;
      out_led_clk <= 0;
      parity <= 0;
    end else begin
      out_clk <= in_clk;
      if (in_clk) begin
        // handle states 
        case (state)
          0: begin // receiving data, if the first bit is 1, move to next state and change the bit to zero
            if (bit_counter == 0 && in_data) begin
              out_data <= ~in_data;
              state <= 1;
              parity <= in_data;
            end else begin
              out_data <= in_data;
            end
          end
          1: begin  // receiving first led data
            if (bit_counter == 31) begin
              out_data <= ~in_data;
              if (in0selected) begin
                if (parity == in_data) begin
                  pwm_set <= !error;
                end else begin
                  error <= 1;
                end
                state <= 3;
              end else begin
                state <= 2;
              end
            end else begin
              out_data <= in_data;
              if (bit_counter != 0) begin
                out_led_clk <= 1;
                parity <= parity ^ in_data;
              end else parity <= in_data;
            end
          end
          2: begin  // receiving LED data 2 byte in BIN mode
            if (bit_counter == 0) begin
              out_data <= ~in_data;
              parity   <= in_data;
              if (!in_data) begin
                error <= 1;
              end
            end else if (bit_counter == 31) begin
              out_data <= ~in_data;
              if (parity == in_data) begin
                pwm_set <= !error;
              end else begin
                error <= 1;
              end
              state <= 3;
            end else begin
              out_data <= in_data;
              out_led_clk <= 1;
              parity <= parity ^ in_data;
            end
          end
          3: begin
            if (bit_counter == 0 && in_data) begin
              error <= 1;
            end
            out_data <= in_data;
            pwm_set  <= 0;
          end
        endcase
      end else begin
        out_led_clk <= 0;
      end
    end
  end
endmodule
