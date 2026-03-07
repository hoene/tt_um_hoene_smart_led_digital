# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_manchester_encoder(dut):

    dut._log.info("Start manchester encoding")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "manchester_encoding")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1
    dut._log.info("test manchester encoding")

    ## much data to DIN
    data = [1] * 64
    await helpers.manchester_encode(data, speed=24, pin=0)

    ## now send one long impulses and two ones
    helpers.decoder_buffer = []
    data = [0, 1] * 64 + [1, 1, 0, 1, 0, 0, 1, 1]
    await helpers.manchester_encode(data, speed=24, pin=0)
    assert helpers.decoder_buffer == data
