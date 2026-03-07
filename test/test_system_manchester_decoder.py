# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_manchester_decoder(dut):

    dut._log.info("Start manchester decoder")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "manchester_decoder")
    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test manchester decoder")

    ## first it is in error state
    assert dut.uo_out.value[4] == 1  # error

    ## send some data of short impulses, but not enough to be valid
    data = [0] * 4
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 1  # error

    ## now send two long impulses
    data = [0, 1, 0, 1]
    await helpers.manchester_encode(data, speed=24, pin=1)

    assert dut.uo_out.value[4] == 0  # no error
    # first bit is lost
    assert helpers.decoder_buffer == [1, 0, 1]

    # test different frequencies

    for speed in [19, 24, 36]:  # lower or higher speed do not work
        helpers.decoder_buffer = []
        data = [1, 0, 0, 1, 0, 1]
        await helpers.manchester_encode(data, speed=speed, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.uo_out.value[4] == 0  # no error

    # send data too slow
    helpers.decoder_buffer = []
    data = [1, 0, 0, 1, 0, 1]
    await helpers.manchester_encode(data, speed=49, pin=1)
    assert dut.uo_out.value[4] == 1  # error

    # try to recover from error state by sending valid data
    data = [1, 0, 1, 0]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error

    # send data too fast
    helpers.decoder_buffer = []
    data = [0, 0, 0]
    await helpers.manchester_encode(
        data, speed=13, pin=1
    )  # TODO: Why do error with 14 to 18 but only wrong data?
    assert dut.uo_out.value[4] == 1  # error
    assert helpers.decoder_buffer != data
