# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic


class Helpers:
    """Various helpers for handling the signals."""

    def __init__(self, dut, test):
        self.dut = dut
        self.test = test

        self.decode_last = Logic("X")
        self.decode_counter = 0
        self.decode_middle = None
        self.decode_data = []
        self.decode_error = True
        self.decode_speed = 24
        self.decoder_buffer = []
        self.pwm_buffer = []
        self.led_red = 0
        self.led_green = 0
        self.led_blue = 0
        self.logs_last_in = ""
        self.logs_last_io = ""
        self.logs_last_out = ""
        self.logs_last_oe = ""
        self.logs_counter = -1

    def manchester_decode(self):
        # Implement the Manchester decoding logic here

        bit = self.dut.uio_out.value[7]
        if bit != self.decode_last:
            # Rising or failing edge detected
            if (
                self.decode_counter >= self.decode_speed * 0.75
                and self.decode_counter <= self.decode_speed * 1.5
            ):
                self.decode_middle = True
                self.decode_error = False
                self.decode_data.append(bit)
            elif (
                self.decode_counter >= self.decode_speed * 1.5
                or self.decode_counter < self.decode_speed * 0.25
            ):
                self.decode_error = True
            elif (
                self.decode_counter < self.decode_speed * 0.75
                and self.decode_counter > 0.25
                and not self.decode_error
            ):
                if not self.decode_middle:
                    self.decode_data.append(bit)
                self.decode_middle = not self.decode_middle
            self.decode_counter = 0

        else:
            self.decode_counter += 1
            if self.decode_counter >= self.decode_speed * 1.5:
                self.decode_error = True
        self.decode_last = bit

    def data_in(self):
        # Read the data from the manchester decoder and log it
        val = self.dut.uo_out.value
        if val[3] == Logic(1) and val[4] == Logic(0):
            self.decoder_buffer.append(
                1 if val[2] == Logic(1) else 0 if val[2] == Logic("0") else "X"
            )

    def pwm_decode(self):
        # Counts the 1024 last IO outputs
        self.pwm_buffer.append(self.dut.uio_out.value)

        # Calculate the duty cycle for each LED
        if len(self.pwm_buffer) > 2048:
            last = self.pwm_buffer.pop(0)
            if last[4] == Logic(1):
                self.led_red -= 1
            if last[5] == Logic(1):
                self.led_green -= 1
            if last[6] == Logic(1):
                self.led_blue -= 1

        if self.dut.uio_out.value[4] == Logic(1):
            self.led_red += 1
        if self.dut.uio_out.value[5] == Logic(1):
            self.led_green += 1
        if self.dut.uio_out.value[6] == Logic(1):
            self.led_blue += 1

    def log_outputs(self):
        # print change changes to the input or output signals
        self.logs_counter += 1
        if (
            self.dut.ui_in.value == self.logs_last_in
            and self.dut.uio_out.value == self.logs_last_io
            and self.dut.uo_out.value == self.logs_last_out
            and self.dut.uio_oe.value == self.logs_last_oe
        ):
            return  # No change in outputs, skip logging

        self.logs_last_in = self.dut.ui_in.value
        self.logs_last_io = self.dut.uio_out.value
        self.logs_last_out = self.dut.uo_out.value
        self.logs_last_oe = self.dut.uio_oe.value
        self.dut._log.debug(
            "%s %6d ui_in=%s uio_out=%s uo_out=%s uio_oe=%s",
            self.test,
            self.logs_counter,
            self.dut.ui_in.value,
            self.dut.uio_out.value,
            self.dut.uo_out.value,
            self.dut.uio_oe.value,
        )

    # Clock one cycle, receive the signals, and log the outputs
    async def one_clock(self):
        await ClockCycles(self.dut.clk, 1)
        self.log_outputs()
        self.manchester_decode()
        self.data_in()
        self.pwm_decode()

    # Clock n times
    async def n_clock(self, n):
        for _ in range(n):
            await self.one_clock()

    # Manchester encoding following IEEE 802.3
    async def manchester_encode(self, data, speed=24, pin=0):
        # Implement the Manchester encoding logic here

        for bit in data:
            if bit == 1:
                val = self.dut.ui_in.value
                val[pin] = 1
                self.dut.ui_in.value = val
                await self.n_clock(speed // 2)
                val = self.dut.ui_in.value
                val[pin] = 0
                self.dut.ui_in.value = val
                await self.n_clock((speed + 1) // 2)
            else:
                val = self.dut.ui_in.value
                val[pin] = 0
                self.dut.ui_in.value = val
                await self.n_clock(speed // 2)
                val = self.dut.ui_in.value
                val[pin] = 1
                self.dut.ui_in.value = val
                await self.n_clock((speed + 1) // 2)
