/*
 * Copyright (c) 2025 Christian Hoene
 * SPDX-License-Identifier: Apache-2.0
 */


`default_nettype none

// select in the data stream which data is used for the LEDs and which data is modified if forwarded
// also, enabled test mode
module tt_um_hoene_protocol_select (
    input in_data,     // input data
    input in_clk,      // input clock
    input in_sync,     // input is valid
    input clk,         // global clock
    input rst_n,     // device reset
    input in0selected, // mode from input selector DIN or BIN
    output reg pwm_set,   // forwarded clock to manachester encoder
    output reg swap_forward_bit, // swap the bit, which is forwarded
    output reg test_mode  // test mode is selected if too many LED data
);
  reg [4:0] bit_counter;
  reg [7:0] led_counter;
  reg pre_state;
  reg out_state;
  reg error;
  reg parity;
  reg modify_state;

  always @(posedge clk) begin
    if (!rst_n) begin
      bit_counter <= 5'b0;
      led_counter <= 8'b0;
      test_mode <= 0;
      swap_forward_bit <= 0;
    end
    /*
    if (!in_sync) begin
      pre_state <= 1;
      out_state <= 0;
      error <= 0;
    end else if (in_clk) begin

      bit_counter <= bit_counter + 1;

// check first bit
      if(bit_counter == 0) begin        // first bit indicate addressed led 
        if(pre_state == 1 && in_data == 1) begin
          pre_state <= 0;
          modify_state <= 1;
          parity <= in_data;
          if(in0selected) begin         
            out_state <= 1;             // DIN selected. Use data
          end
          forward_data <= 0;
        end else if (in_data == 0) begin
            error <= 1;               // error detected
        end else if (modify_state == 1 && out_state == 0) begin
          // BIN selected. Use second data
            out_state <= 1;
        end else begin
            modify_state <= 0;          // finished for here
            out_state <= 0;
        end

// for all intermediate bits shift data to register
      end else if (bit_counter != 31) begin
        parity <= parity ^ in_data;
        shift_out_data <= in_data;
        shift_out_clk <= 1;
      end else begin
        // last bit is parity bit
        if (parity != in_data) begin
          error <= 1;               // parity error detected
        end
        led_pwm_store <= 1;
      end 
    

      

      // check for init state
      if (!insync) begin  // the first byte is 10101011b
        if (last_in == 1 && in_data == 1) begin
          insync <= 1;
        end
      end       
    end
  */
  end
endmodule
