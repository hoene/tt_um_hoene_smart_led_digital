# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_low_pass_filter(dut):

    dut._log.info("Start low pass filter")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "low_pass_filter")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test low pass filter")

    lastbits = [0] * 6
    for loops in range(0, 128):
        for bits in range(0, 7):
            bit = (loops >> bits) & 1

            val = dut.ui_in.value
            val[1] = bit
            dut.ui_in.value = val

            await helpers.n_clock(1)
            # helpers.log_outputs()
            res = dut.uo_out.value[1]
            sum = lastbits[0:5].count(1)
            assert (sum >= 3 and res == 1) or (sum < 3 and res == 0)

            lastbits.append(bit)
            lastbits.pop(0)
