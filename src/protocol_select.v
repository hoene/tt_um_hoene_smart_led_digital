/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_protocol_select (
    input            in_data,           // input data
    input            in_clk,            // input clock
    input            in_sync,           // input is valid
    input            clk,               // global clock
    input            rst_n,             // device reset
    input            in0selected,       // mode from input selector DIN or BIN
    input      [4:0] bit_counter,
    input            parity_error,      // parity enable
    output reg       pwm_set,           // forwarded clock to Manchester encoder
    output reg       swap_forward_bit,  // swap the bit, which is forwarded
    output reg       error,             // error detected
    output reg [1:0] state              // 0->1->[2->]->3->0
);


  always @(posedge clk) begin
    // reset
    if (!rst_n || !in_sync) begin
      swap_forward_bit <= 0;
      state <= 0;
      pwm_set <= 0;
      error <= 0;
    end else if (parity_error) begin
      swap_forward_bit <= 0;
      pwm_set <= 0;
    end else begin
      if (in_clk) begin
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
                pwm_set <= 1;
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
              pwm_set <= 1;
              state <= 3;
            end else begin
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
