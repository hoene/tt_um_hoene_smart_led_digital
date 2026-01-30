/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_protocol_output (
    input            in_data,           // input data
    input            in_clk,            // input clock
    input            in_sync,           // input is valid
    input            clk,               // global clock
    input            rst_n,             // device reset
    input            swap_forward_bit,  // swap the bit, which is forwarded
    output reg       dout            // forwarded clock to Manchester encoder
);
  reg counter 
  always @(posedge clk) begin
    // reset
    if (!rst_n) begin
      dout <= 0;
      counter <= 0;
    end 
    
    if (!rst_n) begin
      out_clk <= 0;
    end else if (!in_sync) begin
      // wait for sync but forward data anyhow
      out_clk <= in_clk;
    end else begin

      // forward data only if not in error state
      if (!error) begin
        out_clk <= in_clk;
      end else begin
        out_clk <= 0;
      end

      // state machine 
      if (error) begin
        swap_forward_bit <= 0;
        pwm_set <= 0;
      end else begin
        // handle states 
        case (state)
          0: begin // receiving data, if the first bit is 1, move to next state and change the bit to zero
            if (bit_counter == 0 && in_data) begin
              swap_forward_bit <= 1;
              state <= 1;
            end
          end
          1: begin  // receiving first led data
            if (bit_counter == 31) begin
              swap_forward_bit <= 1;
              if (in0selected) begin
                pwm_set <= parity == in_data;
                state   <= 3;
              end else begin
                state <= 2;
              end
            end else begin
              swap_forward_bit <= 0;
            end
          end
          2: begin  // receiving LED data 2 byte in BIN mode
            if (bit_counter == 0) begin
              swap_forward_bit <= 1;
              if (!in_data) begin
                error <= 1;
              end
            end else if (bit_counter == 31) begin
              swap_forward_bit <= 1;
              pwm_set <= parity == in_data;
              state <= 3;
            end
            begin
              swap_forward_bit <= 0;
            end
          end
          3: begin
            if (bit_counter == 0 && in_data) begin
              error <= 1;
            end
            swap_forward_bit <= 0;
            pwm_set <= 0;
          end
        endcase
      end
    end
  end
endmodule
