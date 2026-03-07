# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_framing(dut):

    dut._log.info("Start frame detector")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "frame")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test framing")

    assert dut.uo_out.value[5] == 0  # no frame
    assert dut.uo_out.value[4] == 1  # error

    ## now send one long impulses and two ones
    data = [0, 1, 0]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 0]  # first bit is lost
    assert dut.uo_out.value[5] == 0  # frame

    data = [1, 1]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 0, 1, 1]  # first bit is lost
    assert dut.uo_out.value[5] == 1  # frame

    # wait for 42 cycles
    for loops in range(0, 42):
        await helpers.n_clock(1)
        helpers.log_outputs()
        assert dut.uo_out.value[4] == 0  # no error
        assert dut.uo_out.value[5] == 1  # frame should remain until

    # now the timeout starts
    await helpers.n_clock(1)
    helpers.log_outputs()
    assert dut.uo_out.value[4] == 1  # error
    assert dut.uo_out.value[5] == 1  # frame should remain until
    await helpers.n_clock(1)
    helpers.log_outputs()
    assert dut.uo_out.value[4] == 1  # error
    assert dut.uo_out.value[5] == 0
