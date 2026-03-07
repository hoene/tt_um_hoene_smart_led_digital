# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_counters(dut):

    dut._log.info("Start counters")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "counters")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test counters")
    ## now send one long impulses and two ones
    data = [0, 1, 1]
    await helpers.manchester_encode(data, speed=19, pin=1)

    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 1]  # first bit is lost
    assert dut.uo_out.value[5] == 1  # frame

    for bits in range(0, 32):
#        assert dut.user_project.counters_bits.value == bits
        await helpers.manchester_encode([1], speed=19, pin=1)
        assert dut.uo_out.value[6] == 0  # no test

    # send some more data
    for leds in range(0, 131039):
        await helpers.manchester_encode([1], speed=19, pin=1)
        assert dut.uo_out.value[6] == 0  # no test

    # final LED
    await helpers.manchester_encode([1], speed=19, pin=1)
    assert dut.uo_out.value[6] == 1  # test mode should be active after 4096 LEDs
