# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_serial2parallel(dut):
    dut._log.info("serial2parallel start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for loops in range(0, 2):
        # Reset
        dut._log.debug("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.serial2parallel_data.value = 0
        dut.serial2parallel_clk.value = 0
        dut.serial2parallel_store.value = 0

        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.serial2parallel_out.value == 0

        # start
        dut._log.debug("Starting")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.serial2parallel_out.value == 0

        dut._log.debug("shift in 30 bits and store them immediately")
        goal = 0
        for bits in range(0, 30):
            dut.serial2parallel_data.value = bits % 2
            dut.serial2parallel_clk.value = 1
            await ClockCycles(dut.clk, 1)
            dut.serial2parallel_clk.value = 0
            await ClockCycles(dut.clk, 1)
            assert dut.serial2parallel_out.value == goal
            dut.serial2parallel_store.value = 1
            await ClockCycles(dut.clk, 1)
            dut.serial2parallel_store.value = 0
            await ClockCycles(dut.clk, 1)
            goal = goal >> 1 | (bits % 2) << 29
            assert dut.serial2parallel_out.value == goal

        old = goal
        dut._log.debug("shift in 30 bits do not store them")
        for bits in range(0, 30):
            dut.serial2parallel_data.value = (bits & 2) >> 1
            dut.serial2parallel_clk.value = 1
            await ClockCycles(dut.clk, 1)
            dut.serial2parallel_clk.value = 0
            await ClockCycles(dut.clk, 1)
            assert dut.serial2parallel_out.value == old
            goal = goal >> 1 | (bits & 2) << 28

        dut._log.debug("store the data and see whether the output matches")
        dut.serial2parallel_store.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.serial2parallel_out.value == old
        dut.serial2parallel_store.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.serial2parallel_out.value == goal
