# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_input_selector(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for loops in range(0,2):
        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.input_selector_in0.value = 0
        dut.input_selector_in1.value  = 0
        dut.input_selector_testmode.value= 0

        await ClockCycles(dut.clk, 2)

        # check output signals    
        assert dut.input_selector_out.value == 0
        assert dut.input_selector_in0selected.value == 0

        # start
        dut._log.info("Starting")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 1)

        # check output signals    
        assert dut.input_selector_out.value == 0
        assert dut.input_selector_in0selected.value== 0

        # check input 1 
        dut._log.info("Input 1 testing")
        assert dut.input_selector_in0selected.value == 0
        for i in range(0,4):
            dut.input_selector_in1.value  = 1
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 1
            dut.input_selector_in1.value  = 0
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0

        # check testmode input 0
        dut._log.info("Testmode Input 0")
        dut.input_selector_testmode.value = 1
        await ClockCycles(dut.clk, 2)
        assert dut.input_selector_in0selected.value == 1
        assert dut.input_selector_out.value == 0
        
        for i in range(0,4):
            dut.input_selector_in0.value = 1
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 1
            dut.input_selector_in0.value = 0
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0

        # check testmode input 0
        dut._log.info("Disable testmode Input 0")
        dut.input_selector_testmode.value = 0
        await ClockCycles(dut.clk, 2)
        assert dut.input_selector_in0selected.value== 0

        for i in range(0,59):
            dut.input_selector_in0.value = 1
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0
            assert dut.input_selector_in0selected.value== 0
            dut.input_selector_in0.value = 0
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0

        for i in range(0,100):
            dut.input_selector_in0.value = 1
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 1
            assert dut.input_selector_in0selected.value== 1
            dut.input_selector_in0.value = 0
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0

        # wait for input 0 to be come selected
        assert dut.input_selector_out.value == 0

        dut._log.info("Testmode Input 1")
        dut.input_selector_testmode.value = 1
        await ClockCycles(dut.clk, 2)
        assert dut.input_selector_in0selected.value== 0
        for i in range(0,3):
            dut.input_selector_in1.value  = 1
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 1
            dut.input_selector_in1.value  = 0
            await ClockCycles(dut.clk, 2)
            assert dut.input_selector_out.value == 0
