# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
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
#        assert dut.user_project.counters_bits.value == 0
        assert  dut.uio_out.value[1:0] == 0

        helpers.decoder_buffer = []
        data = [1]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
#        assert dut.user_project.counters_bits.value == 1
        assert dut.uio_out.value[1:0] == 1
        assert dut.uio_out.value[3] == 0  # data output inverse

        helpers.decoder_buffer = []
        data = [1] * 11 + [0] * 14 + [1] * 5
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
#        assert dut.user_project.counters_bits.value == 31
        assert dut.uio_out.value[1:0] == 1
        assert dut.uio_out.value[3] == 1  # data output normal

        helpers.decoder_buffer = []
        data = [1]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
#        assert dut.user_project.counters_bits.value == 0
        assert dut.uio_out.value[1:0] == 2
        assert dut.uio_out.value[3] == 0  # data output inverse

        # second LED word
        helpers.decoder_buffer = []
        data = [1] * 12 + [0] * 14 + [1] * 5 + [parity]
        await helpers.manchester_encode(data, speed=19, pin=1)
        assert helpers.decoder_buffer == data
#        assert dut.user_project.counters_bits.value == 0
        assert dut.uio_out.value[1:0] == 3
        assert dut.uio_out.value[3] == 1 - parity  # data output inverse
        assert dut.uo_out.value[7] == parity  # PWM_SET
