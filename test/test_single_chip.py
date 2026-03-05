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
        # Counts the 16384 last IO outputs
        self.pwm_buffer.append(self.dut.uio_out.value)

        # Calculate the duty cycle for each LED
        if len(self.pwm_buffer) > 16384:
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
        self.dut._log.info(
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


# @cocotb.test()
async def test_input_selector(dut):

    for loops in range(0, 2):

        dut._log.info("Start input selector test %s", loops)

        # Set the clock period to 41.67 ns (24 MHz)
        clock = Clock(dut.clk, 42, unit="ns")
        cocotb.start_soon(clock.start())

        helpers = Helpers(dut, "input_selector" + str(loops))

        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0

        await helpers.n_clock(10)
        dut.rst_n.value = 1

        dut._log.info("Test input selector on pin 0, needs 64 toggles")

        data = [1] * (254 + loops)
        await helpers.manchester_encode(data, speed=24, pin=1)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1] * 62
        await helpers.manchester_encode(data, speed=24, pin=0)
        # no IN0Selected, so output should be 0
        assert dut.uo_out.value[0] == 0

        data = [1]
        await helpers.manchester_encode(data, speed=24, pin=0)
        assert dut.uo_out.value[0] == 1 - loops


# @cocotb.test()
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


# @cocotb.test()
async def test_manchester_decoder(dut):

    dut._log.info("Start manchester decoder")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "manchester_decoder")
    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test manchester decoder")

    ## first it is in error state
    assert dut.uo_out.value[4] == 1  # error

    ## send some data of short impulses, but not enough to be valid
    data = [0] * 4
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 1  # error

    ## now send two long impulses
    data = [0, 1, 0, 1]
    await helpers.manchester_encode(data, speed=24, pin=1)

    assert dut.uo_out.value[4] == 0  # no error
    # first bit is lost
    assert helpers.decoder_buffer == [1, 0, 1]

    # test different frequencies

    for speed in [19, 24, 36]:  # lower or higher speed do not work
        helpers.decoder_buffer = []
        data = [1, 0, 0, 1, 0, 1]
        await helpers.manchester_encode(data, speed=speed, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.uo_out.value[4] == 0  # no error

    # send data too slow
    helpers.decoder_buffer = []
    data = [1, 0, 0, 1, 0, 1]
    await helpers.manchester_encode(data, speed=49, pin=1)
    assert dut.uo_out.value[4] == 1  # error

    # try to recover from error state by sending valid data
    data = [1, 0, 1, 0]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error

    # send data too fast
    helpers.decoder_buffer = []
    data = [0, 0, 0]
    await helpers.manchester_encode(
        data, speed=13, pin=1
    )  # TODO: Why do error with 14 to 18 but only wrong data?
    assert dut.uo_out.value[4] == 1  # error
    assert helpers.decoder_buffer != data


# @cocotb.test()
async def test_framing(dut):

    dut._log.info("Start frame detector")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "frame")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test framing")

    assert dut.uo_out.value[5] == 0  # no frame
    assert dut.uo_out.value[4] == 1  # error

    ## now send one long impulses and two ones
    data = [0, 1, 0]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 0]  # first bit is lost
    assert dut.uo_out.value[5] == 0  # frame

    data = [1, 1]
    await helpers.manchester_encode(data, speed=24, pin=1)
    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 0, 1, 1]  # first bit is lost
    assert dut.uo_out.value[5] == 1  # frame

    # wait for 42 cycles
    for loops in range(0, 42):
        await helpers.n_clock(1)
        helpers.log_outputs()
        assert dut.uo_out.value[4] == 0  # no error
        assert dut.uo_out.value[5] == 1  # frame should remain until

    # now the timeout starts
    await helpers.n_clock(1)
    helpers.log_outputs()
    assert dut.uo_out.value[4] == 1  # error
    assert dut.uo_out.value[5] == 1  # frame should remain until
    await helpers.n_clock(1)
    helpers.log_outputs()
    assert dut.uo_out.value[4] == 1  # error
    assert dut.uo_out.value[5] == 0


# @cocotb.test()
async def test_counters(dut):

    dut._log.info("Start counters")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "counters")

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await helpers.n_clock(10)
    dut.rst_n.value = 1

    dut._log.info("test counters")
    ## now send one long impulses and two ones
    data = [0, 1, 1]
    await helpers.manchester_encode(data, speed=19, pin=1)

    assert dut.uo_out.value[4] == 0  # no error
    assert helpers.decoder_buffer == [1, 1]  # first bit is lost
    assert dut.uo_out.value[5] == 1  # frame

    for bits in range(0, 32):
        assert dut.user_project.counters_bits.value == bits
        await helpers.manchester_encode([1], speed=19, pin=1)
        assert dut.uo_out.value[6] == 0  # no test

    # send some more data
    for leds in range(0, 131039):
        await helpers.manchester_encode([1], speed=19, pin=1)
        assert dut.uo_out.value[6] == 0  # no test

    # final LED
    await helpers.manchester_encode([1], speed=19, pin=1)
    assert dut.uo_out.value[6] == 1  # test mode should be active after 4096 LEDs


# @cocotb.test()
async def test_protocol_bin(dut):

    dut._log.info("Start protocol bin")

    for parity in range(0, 2):
        # Set the clock period to 41.67 ns (24 MHz)
        clock = Clock(dut.clk, 42, unit="ns")
        cocotb.start_soon(clock.start())

        helpers = Helpers(dut, "protocol_bin_" + str(parity))

        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0

        await helpers.n_clock(10)
        dut.rst_n.value = 1

        dut._log.info("test protocol")
        ## now send one long impulses and two ones
        data = [0, 1, 1]
        await helpers.manchester_encode(data, speed=19, pin=1)

        assert dut.uo_out.value[4] == 0  # no error
        assert helpers.decoder_buffer == [1, 1]  # first bit is lost
        assert dut.uo_out.value[5] == 1  # frame
        assert dut.user_project.counters_bits.value == 0
        assert dut.user_project.protocol_state.value == 0

        helpers.decoder_buffer = []
        data = [1]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 1
        assert dut.user_project.protocol_state.value == 1
        assert dut.uio_out.value[3] == 0  # data output inverse

        helpers.decoder_buffer = []
        data = [1] * 11 + [0] * 14 + [1] * 5
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 31
        assert dut.user_project.protocol_state.value == 1
        assert dut.uio_out.value[3] == 1  # data output normal

        helpers.decoder_buffer = []
        data = [1]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 0
        assert dut.user_project.protocol_state.value == 2
        assert dut.uio_out.value[3] == 0  # data output inverse

        # second LED word
        print(parity)
        helpers.decoder_buffer = []
        data = [1] * 12 + [0] * 14 + [1] * 5 + [parity]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 0
        assert dut.user_project.protocol_state.value == 3
        assert dut.uio_out.value[3] == 1 - parity  # data output inverse
        assert dut.uo_out.value[7] == parity  # PWM_SET


@cocotb.test()
async def test_protocol_din(dut):

    dut._log.info("Start protocol din")

    for parity in range(0, 2):
        # Set the clock period to 41.67 ns (24 MHz)
        clock = Clock(dut.clk, 42, unit="ns")
        cocotb.start_soon(clock.start())

        helpers = Helpers(dut, "protocol_din_" + str(parity))

        # Reset
        dut._log.info("Reset")
        dut.ena.value = 1
        dut.ui_in.value = 0
        dut.uio_in.value = 0
        dut.rst_n.value = 0

        await helpers.n_clock(10)
        dut.rst_n.value = 1
        dut._log.info("test protocol din")
        ## now send one long impulses and two ones
        data = [0, 1] * 64 + [1]
        await helpers.manchester_encode(data, speed=19, pin=0)

        assert dut.uo_out.value[4] == 0  # no error
        assert helpers.decoder_buffer[-2:] == [1, 1]  # first bit is lost
        assert dut.uo_out.value[5] == 1  # frame
        assert dut.user_project.counters_bits.value == 0
        assert dut.user_project.protocol_state.value == 0

        helpers.decoder_buffer = []
        data = [1]
        await helpers.manchester_encode(data, speed=19, pin=0)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 1
        assert dut.user_project.protocol_state.value == 1
        assert dut.uio_out.value[3] == 0  # data output inverse

        helpers.decoder_buffer = []
        data = [1] * 11 + [0] * 14 + [1] * 5
        await helpers.manchester_encode(data, speed=19, pin=0)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 31
        assert dut.user_project.protocol_state.value == 1
        assert dut.uio_out.value[3] == 1  # data output normal

        helpers.decoder_buffer = []
        data = [parity]
        await helpers.manchester_encode(data, speed=19, pin=0)
        assert helpers.decoder_buffer == data
        assert dut.user_project.counters_bits.value == 0
        assert dut.user_project.protocol_state.value == 3
        assert dut.uio_out.value[3] == 1 - parity  # data output inverse
        assert dut.uo_out.value[7] == parity  # PWM_SET
