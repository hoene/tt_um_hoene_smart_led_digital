# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

BIT_LENGTH = 24  # must match the value in manchester_decoder.v


@cocotb.test()
async def test_manchester_decoder_init(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for pulsewidth in range(1, BIT_LENGTH * 2):
        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.manchester_decoder_in.value = 0

        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 1

        # start
        dut._log.info("first pulse %d", pulsewidth)
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 1

        # first long pulse
        dut.manchester_decoder_in.value = 1
        await ClockCycles(dut.clk, pulsewidth)
        dut.manchester_decoder_in.value = 0
        await ClockCycles(dut.clk, 2)

        if pulsewidth <= BIT_LENGTH * 0.75:
            # too short initial pulse -> remain in error state
            assert dut.manchester_decoder_out_clk.value == 0
            assert dut.manchester_decoder_out_data.value == 0
            assert dut.manchester_decoder_out_error.value == 1
        elif pulsewidth <= BIT_LENGTH * 1.5:
            # too short initial pulse -> remain in error state
            assert dut.manchester_decoder_out_clk.value == 1
            assert dut.manchester_decoder_out_data.value == 1
            assert dut.manchester_decoder_out_error.value == 0
        else:
            # too short initial pulse -> remain in error state
            assert dut.manchester_decoder_out_clk.value == 0
            assert dut.manchester_decoder_out_data.value == 0
            assert dut.manchester_decoder_out_error.value == 1
