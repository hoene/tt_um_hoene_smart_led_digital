# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic

decode_last = Logic("X")
decode_counter = 0
decode_middle = None
decode_data = []
decode_error = True
decode_speed = 24


def manchester_decode(dut):
    # Implement the Manchester decoding logic here
    global decode_last, decode_counter, decode_middle, decode_data, decode_error

    bit = dut.uio_out.value[7]
    if bit != decode_last:
        # Rising or failing edge detected
        if (
            decode_counter >= decode_speed * 0.75
            and decode_counter <= decode_speed * 1.5
        ):
            decode_middle = True
            decode_error = False
            decode_data.append(bit)
        elif (
            decode_counter >= decode_speed * 1.5 or decode_counter < decode_speed * 0.25
        ):
            decode_error = True
        elif (
            decode_counter < decode_speed * 0.75
            and decode_counter > 0.25
            and not decode_error
        ):
            if not decode_middle:
                decode_data.append(bit)
            decode_middle = not decode_middle
        decode_counter = 0

    else:
        decode_counter += 1
        if decode_counter >= decode_speed * 1.5:
            decode_error = True
    decode_last = bit


pwm_buffer = []
led_red = 0
led_green = 0
led_blue = 0


def pwm_decode(dut):
    # Counts the 16384 last IO outputs
    global pwm_buffer, led_red, led_green, led_blue
    pwm_buffer.append(dut.uio_out.value)

    # Calculate the duty cycle for each LED
    if len(pwm_buffer) > 16384:
        last = pwm_buffer.pop(0)
        if last[4] == Logic(1):
            led_red -= 1
        if last[5] == Logic(1):
            led_green -= 1
        if last[6] == Logic(1):
            led_blue -= 1

    if dut.uio_out.value[4] == Logic(1):
        led_red += 1
    if dut.uio_out.value[5] == Logic(1):
        led_green += 1
    if dut.uio_out.value[6] == Logic(1):
        led_blue += 1


logs_last_in = ""
logs_last_io = ""
logs_last_out = ""
logs_last_oe = ""
counter = -1


def log_outputs(dut):
    # print change changes to the input or output signals
    global logs_last_in, logs_last_io, logs_last_out, logs_last_oe, counter
    counter += 1
    if (
        dut.ui_in.value == logs_last_in
        and dut.uio_out.value == logs_last_io
        and dut.uo_out.value == logs_last_out
        and dut.uio_oe.value == logs_last_oe
    ):
        return  # No change in outputs, skip logging

    logs_last_in = dut.ui_in.value
    logs_last_io = dut.uio_out.value
    logs_last_out = dut.uo_out.value
    logs_last_oe = dut.uio_oe.value
    print(
        counter,
        dut.user_project.ui_in.value,
        dut.user_project.uio_out.value,
        dut.user_project.uo_out.value,
        dut.user_project.uio_oe.value,
    )


# Clock one cycle, receive the signals, and log the outputs
async def one_clock(dut):
    await ClockCycles(dut.clk, 1)
    log_outputs(dut)
    manchester_decode(dut)
    pwm_decode(dut)


# Clock n times
async def n_clock(dut, n):
    for _ in range(n):
        await one_clock(dut)


# Manchester encoding following IEEE 802.3
async def manchester_encode(dut, data, speed=24, pin=0):
    # Implement the Manchester encoding logic here

    for bit in data:
        if bit == 0:
            val = dut.ui_in.value
            val[pin] = 1
            dut.ui_in.value = val
            await n_clock(dut, speed // 2)
            val = dut.ui_in.value
            val[pin] = 0
            dut.ui_in.value = val
            await n_clock(dut, (speed + 1) // 2)
        else:
            val = dut.ui_in.value
            val[pin] = 0
            dut.ui_in.value = val
            await n_clock(dut, speed // 2)
            val = dut.ui_in.value
            val[pin] = 1
            dut.ui_in.value = val
            await n_clock(dut, (speed + 1) // 2)


@cocotb.test()
async def test_input_selector0(dut):

    for loops in range(0, 2):

        dut._log.info("Start input selector test", loops)

        # Set the clock period to 41.67 ns (24 MHz)
        clock = Clock(dut.clk, 42, unit="ns")
        cocotb.start_soon(clock.start())

        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0

        await n_clock(dut, 10)
        dut.rst_n.value = 1

        dut._log.info("Test input selector on pin 0, needs 64 toggles")

        data = [1] * (254 + loops)
        await manchester_encode(dut, data, speed=24, pin=1)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1] * 62
        await manchester_encode(dut, data, speed=24, pin=0)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1]
        await manchester_encode(dut, data, speed=24, pin=0)
        assert dut.uo_out.value[0] == 1 - loops
