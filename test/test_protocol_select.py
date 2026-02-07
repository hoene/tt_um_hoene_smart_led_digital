# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_protocol_select_bin(dut):
    dut._log.info("protocol select bin start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.debug("Reset")
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_in_clk.value = 0
    dut.protocol_select_in_sync.value = 0
    dut.protocol_select_in0selected.value = 0
    dut.protocol_select_bits.value = 0

    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # start
    dut._log.debug("Starting")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # bit 0 is one, insync is zero,
    dut.protocol_select_in_data.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # bit 0 is one, insync is one
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_in_sync.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # bit 0 is one, insync is one, bits is 2
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 2
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # first LED data
    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 0
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 1

    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 1

    # insync is one, bits is 31, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 31
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 2

    # second LED data
    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 0
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 2

    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 2

    # insync is one, bits is 31, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 31
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 1
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 3

    # insync is one, bits is 31, data is one -> first LED data
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_bits.value = 0
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)


@cocotb.test()
async def test_protocol_select_din(dut):
    dut._log.info("protocol select din start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.debug("Reset")
    dut.ena.value = 1
    dut.rst_n.value = 0
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_in_clk.value = 0
    dut.protocol_select_in_sync.value = 0
    dut.protocol_select_in0selected.value = 1
    dut.protocol_select_bits.value = 0

    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # start
    dut._log.debug("Starting")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # bit 0 is one, insync is one
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_in_sync.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # bit 0 is one, insync is one, bits is 2
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 2
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 0

    # first LED data
    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 0
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 1

    # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 1

    # insync is one, bits is 31, data is one -> first LED data
    dut.protocol_select_in_data.value = 1
    dut.protocol_select_bits.value = 31
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 1
    assert dut.protocol_select_swap_forward_bit.value == 1
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 3

    # insync is one, bits is 0, data is one -> first LED data
    dut.protocol_select_in_data.value = 0
    dut.protocol_select_bits.value = 0
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 1
    await ClockCycles(dut.clk, 1)
    dut.protocol_select_in_clk.value = 0
    await ClockCycles(dut.clk, 1)

    # check output signals
    assert dut.protocol_select_pwm_set.value == 0
    assert dut.protocol_select_swap_forward_bit.value == 0
    assert dut.protocol_select_error.value == 0
    assert dut.protocol_select_state.value == 3
