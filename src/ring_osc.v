`default_nettype none

// Originally this was designed for TT09 on sky130, using the sky130_fd_sc_hd__inv_2 cell.
// See: https://github.com/algofoogle/tt09-ring-osc2/commit/ee2feec185f6f5ddf48dfbf057093a3cfc8f5dea
// It was rehardened for TTIHP25a using a sky130 "polyfill" (mapping sky130 cells to equivalent
// cells or logic in the IHP PDK).
// See: https://github.com/TinyTapeout/tt09-ttihp25a-reharden/blob/cfa0e6adf57c4bb4c5f6ec924ec0cc5bfb1fdfe2/hdl/tt_um_algofoogle_tt09_ring_osc2/src/sky130_polyfill.v#L389
// Hence, where you see sky130_fd_sc_hd__inv_2 below, it maps instead to a logical complement, which in turn
// maps to some IHP inverter cell.

// copied from https://github.com/algofoogle/tt09-ring-osc2
// thanks to Anton Maurovic


module polyfill__inv(input A, output Y); assign Y = ~A; endmodule

module amm_inverter (
    input  wire a,
    output wire y
);

  (* keep_hierarchy *) polyfill__inv sky_inverter (
      .A(a),
      .Y(y)
  );

endmodule

module ring_osc #(
    parameter DEPTH = 500  // Becomes DEPTH*2+1 inverters to ensure it is odd.
) (
    input wire ena,
    output osc_out
);

  wire [DEPTH*2:0] inv_in;
  wire [DEPTH*2:0] inv_out;
  assign inv_in[DEPTH*2:1] = inv_out[DEPTH*2-1:0];  // Chain.
  assign inv_in[0] = inv_out[DEPTH*2] & ena;  // Loop back.
  // Generate an instance array of inverters, chained and looped back via the 2 assignments above:
  (* keep_hierarchy *)
  amm_inverter inv_array[DEPTH*2:0] (
      .a(inv_in),
      .y(inv_out)
  );
  assign osc_out = inv_in[0];

endmodule
