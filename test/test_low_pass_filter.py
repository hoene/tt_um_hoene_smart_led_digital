# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_low_pass_filter(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for loops in range(0,2):
        # Reset
        dut._log.debug("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.low_pass_filter_in.value = 0

        await ClockCycles(dut.clk, 2)

        # check output signals    
        assert dut.low_pass_filter_out.value == 0

        # start
        dut._log.debug("Starting")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals    
        assert dut.low_pass_filter_out.value == 0

        last1 = 0
        last0 = 0
        exp = 0
        # check input 1 
        dut._log.debug("low pass filtering")
        for i in range(0,32):
            for b in range(0,5):
                out = (i >> b) & 1
                dut.low_pass_filter_in.value = out
                await ClockCycles(dut.clk, 1)
                assert exp == dut.low_pass_filter_out.value

                # prepare values for new cycle
                if out+last0+last1 >= 2:
                    exp = 1
                else:
                    exp = 0
                last1=last0
                last0=out
