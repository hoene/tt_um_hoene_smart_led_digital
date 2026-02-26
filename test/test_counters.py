# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_counters(dut):
    dut._log.info("counters start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.debug("Reset")
    dut.ena.value = 1
    dut.counters_in_frame.value = 0
    dut.counters_in_clk.value = 0
    dut.counters_in_data.value = 0

    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.counters_bits.value == 0
    assert dut.counters_test_mode.value == 0
    assert dut.counters_out_clk.value == 0
    assert dut.counters_out_data.value == 0

    # start
    dut._log.debug("Starting ")
    dut.counters_in_frame.value = 1
    await ClockCycles(dut.clk, 1)

    for i in range(1, 32):
        dut.counters_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.counters_out_clk.value == 0
        assert dut.counters_out_data.value == 0

        dut.counters_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        assert dut.counters_out_clk.value == 1
        assert dut.counters_out_data.value == 0
        assert dut.counters_bits.value == i
        assert dut.counters_test_mode.value == 0

    for j in range(0, 4095):
        for i in range(0, 32):
            dut.counters_in_clk.value = 1
            dut.counters_in_data.value = (j + i) & 1
            await ClockCycles(dut.clk, 1)
            assert dut.counters_out_clk.value == 0
            dut.counters_in_clk.value = 0
            await ClockCycles(dut.clk, 1)
            assert dut.counters_out_clk.value == 1
            assert dut.counters_out_data.value == (j + i) & 1
            assert dut.counters_bits.value == i
            assert dut.counters_test_mode.value == 0

    for i in range(0, 40):
        dut.counters_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.counters_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        assert dut.counters_bits.value == i % 0x20
        assert dut.counters_test_mode.value == 1
