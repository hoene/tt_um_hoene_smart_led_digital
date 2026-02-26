# SPDX-FileCopyrightText: © 2025 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_protocol_din(dut):
    dut._log.info("protocol select din start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    for parity in range(0, 2):
        # Reset
        dut._log.debug("Reset")
        dut.ena.value = 1
        dut.rst_n.value = 0
        dut.protocol_in_data.value = 0
        dut.protocol_in_clk.value = 0
        dut.protocol_in_frame.value = 0
        dut.protocol_in0selected.value = 1
        dut.protocol_bits.value = 0

        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_data.value == 0
        assert dut.protocol_out_clk.value == 0
        assert dut.protocol_out_led_clk.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 0

        # start
        dut._log.debug("Starting")
        dut.rst_n.value = 1
        await ClockCycles(dut.clk, 2)

        # check output signals
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_data.value == 0
        assert dut.protocol_out_clk.value == 0
        assert dut.protocol_out_led_clk.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 0

        # bit 0 is one, insync is zero,
        dut.protocol_in_data.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_out_data.value == 0
        assert dut.protocol_out_clk.value == 0
        assert dut.protocol_out_led_clk.value == 0

        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_out_data.value == 1
        assert dut.protocol_out_clk.value == 0
        assert dut.protocol_out_led_clk.value == 0

        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_out_data.value == 1
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 0

        # bit 0 is one, framing is one
        dut.protocol_in_data.value = 0
        dut.protocol_in_frame.value = 1
        await ClockCycles(dut.clk, 1)

        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_out_clk.value == 0

        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        # check output signals
        assert dut.protocol_out_data.value == 0
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 0
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 0

        # bit 0 is one, insync is one, bits is 2
        dut.protocol_in_data.value = 1
        dut.protocol_bits.value = 2
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        # check output signals
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_out_data.value == 1
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 0
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 0

        # first LED data
        # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
        dut.protocol_in_data.value = 1
        dut.protocol_bits.value = 0
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        # check output signals
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_out_data.value == 0  # bit is swipped
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 1
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 0

        # bit 0 is one, insync is one, bits is 0, data is one -> first LED data
        dut.protocol_in_data.value = 1
        dut.protocol_bits.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 0
        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        # check output signals
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_out_led_clk.value == 1
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_out_data.value == 1
        assert dut.protocol_pwm_set.value == 0
        assert dut.protocol_error.value == 0
        assert dut.protocol_state.value == 1

        # insync is one, bits is 31, data is one -> first LED data
        dut.protocol_in_data.value = parity
        dut.protocol_bits.value = 31
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)

        # check output signals
        assert dut.protocol_out_led_clk.value == 0
        assert dut.protocol_out_clk.value == 1
        assert dut.protocol_out_data.value == 1 - parity
        assert dut.protocol_pwm_set.value == 1 - parity
        assert dut.protocol_error.value == parity
        assert dut.protocol_state.value == 3

        # insync is one, bits is 31, data is one -> first LED data
        dut.protocol_in_data.value = 0
        dut.protocol_bits.value = 0
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 1
        await ClockCycles(dut.clk, 1)
        dut.protocol_in_clk.value = 0
        await ClockCycles(dut.clk, 1)
