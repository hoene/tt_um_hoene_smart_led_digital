# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

BIT_LENGTH = 22  # must match the value in manchester_decoder.v


@cocotb.test()
async def test_manchester_encoder(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.debug("Reset")
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.manchester_encoder_in_data.value = 0
    dut.manchester_encoder_in_clk.value = 0
    dut.manchester_encoder_in_error.value = 0
    dut.manchester_encoder_in_pulsewidth.value = BIT_LENGTH
    
    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.manchester_encoder_out_data.value == 0
    assert dut.manchester_encoder_out_enable.value == 0
    
    # start
    for i in range(0, 2):
        dut._log.debug(f"starting iteration {i}")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.manchester_encoder_out_data.value == 0
        assert dut.manchester_encoder_out_enable.value == 0

        # start
        dut._log.debug("first bit 1")
        dut.manchester_encoder_in_data.value = 1
        dut.manchester_encoder_in_clk.value = 1
        dut.manchester_encoder_in_error.value = 0
        await ClockCycles(dut.clk, 1)
        dut.manchester_encoder_in_clk.value = 0

        # check output signals
        for i in range(0, BIT_LENGTH//2 + 1):
            await ClockCycles(dut.clk, 1)
            assert dut.manchester_encoder_out_data.value == 1
            assert dut.manchester_encoder_out_enable.value == 1

        for i in range(0, BIT_LENGTH):
            await ClockCycles(dut.clk, 1)
            assert dut.manchester_encoder_out_data.value == 0
            assert dut.manchester_encoder_out_enable.value == 1

        # start
        dut._log.debug("second bit 0")
        dut.manchester_encoder_in_data.value = 0
        dut.manchester_encoder_in_clk.value = 1
        dut.manchester_encoder_in_error.value = 0
        await ClockCycles(dut.clk, 1)
        dut.manchester_encoder_in_clk.value = 0

        # check output signals
        for i in range(0, BIT_LENGTH//2 + 1):
            await ClockCycles(dut.clk, 1)
            assert dut.manchester_encoder_out_data.value == 0
            assert dut.manchester_encoder_out_enable.value == 1

        for i in range(0, BIT_LENGTH):
            await ClockCycles(dut.clk, 1)
            assert dut.manchester_encoder_out_data.value == 1
            assert dut.manchester_encoder_out_enable.value == 1

        # start
        dut._log.debug("error")
        dut.manchester_encoder_in_data.value = 0
        dut.manchester_encoder_in_clk.value = 1
        dut.manchester_encoder_in_error.value = 1
        await ClockCycles(dut.clk, 1)
        dut.manchester_encoder_in_clk.value = 0

        # check output signals
        for i in range(0, BIT_LENGTH):
            await ClockCycles(dut.clk, 1)
            assert dut.manchester_encoder_out_enable.value == 0

