# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_protocol_select(dut):
    dut._log.info("protocol select start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for loops in range(0, 2):
        # Reset
        dut._log.debug("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.protocol_insync_data.value = 0
        dut.protocol_insync_clk.value = 0
        dut.protocol_insync_error.value = 0

        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.protocol_insync_out.value == 0

        # start
        dut._log.debug("Starting")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.protocol_insync_out.value == 0

        # zero input
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 0

        # one input
        dut.protocol_insync_data.value = 1
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 0

        # zero input 2
        dut.protocol_insync_data.value = 0
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 0

        # zero input 3
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 0

        # one input 2
        dut.protocol_insync_data.value = 1
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 0

        # one input 3
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 2)
        assert dut.protocol_insync_out.value == 1

        # zero input 4
        dut.protocol_insync_data.value = 0
        dut.protocol_insync_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_insync_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_insync_out.value == 1

        if loops == 2:
            # in_error
            dut.protocol_insync_error.value = 1
            await ClockCycles(dut.clk, 2)
            assert dut.protocol_insync_out.value == 0
