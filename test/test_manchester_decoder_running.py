# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

BIT_LENGTH = 24  # must match the value in manchester_decoder.v


@cocotb.test()
async def test_manchester_decoder_running(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for loop in range(1, 3):
        # Reset
        dut._log.debug("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.manchester_decoder_in.value = 0

        await ClockCycles(dut.clk, 2)

        # start
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # first long 1 pulse
        dut._log.debug("1 long")
        dut.manchester_decoder_in.value = 1
        await ClockCycles(dut.clk, BIT_LENGTH)
        dut.manchester_decoder_in.value = 0
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 1
        assert dut.manchester_decoder_out_data.value == 1
        assert dut.manchester_decoder_out_error.value == 0

        # clock valid only for one cycle
        await ClockCycles(dut.clk, 1)
        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # long 0 pulse
        dut._log.debug("0 long")
        await ClockCycles(dut.clk, BIT_LENGTH)
        dut.manchester_decoder_in.value = 1
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 1
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # clock valid only for one cycle
        await ClockCycles(dut.clk, 1)
        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # short 1 pulse
        dut._log.debug("1 short")

        await ClockCycles(dut.clk, BIT_LENGTH >> 1)
        dut.manchester_decoder_in.value = 0
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # short 0 pulse
        dut._log.debug("0 short")
        await ClockCycles(dut.clk, BIT_LENGTH >> 1)
        dut.manchester_decoder_in.value = 1
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 1
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # too short 1 pulse
        dut._log.debug("1 spike")
        await ClockCycles(dut.clk, 2)
        dut.manchester_decoder_in.value = 0
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 1

        # long 0 pulse
        dut._log.debug("0 long")
        await ClockCycles(dut.clk, BIT_LENGTH)
        dut.manchester_decoder_in.value = 1
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 1
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 0

        # too long 1 pulse
        dut._log.debug("1 too long")
        await ClockCycles(dut.clk, 2 * BIT_LENGTH)
        dut.manchester_decoder_in.value = 0
        await ClockCycles(dut.clk, 2)

        assert dut.manchester_decoder_out_clk.value == 0
        assert dut.manchester_decoder_out_data.value == 0
        assert dut.manchester_decoder_out_error.value == 1
