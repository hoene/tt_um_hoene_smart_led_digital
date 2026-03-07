# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_input_selector(dut):

    for loops in range(0, 2):

        dut._log.info("Start input selector test %s", loops)

        # Set the clock period to 41.67 ns (24 MHz)
        clock = Clock(dut.clk, 42, unit="ns")
        cocotb.start_soon(clock.start())

        helpers = Helpers(dut, "input_selector" + str(loops))

        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0

        await helpers.n_clock(10)
        dut.rst_n.value = 1

        dut._log.info("Test input selector on pin 0, needs 64 toggles")

        data = [1] * (254 + loops)
        await helpers.manchester_encode(data, speed=24, pin=1)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1] * 62
        await helpers.manchester_encode(data, speed=24, pin=0)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1]
        await helpers.manchester_encode(data, speed=24, pin=0)
        assert dut.uo_out.value[0] == 1 - loops
