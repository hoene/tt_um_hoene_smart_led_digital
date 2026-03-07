# SPDX-FileCopyrightText: © 2026 Christian Hoene
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.types import Logic
from helpers import Helpers


@cocotb.test()
async def test_serial2parallel(dut):

    dut._log.info("Start protocol din")

    # Set the clock period to 41.67 ns (24 MHz)
    clock = Clock(dut.clk, 42, unit="ns")
    cocotb.start_soon(clock.start())

    helpers = Helpers(dut, "serial2parallel")

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
#    assert dut.user_project.counters_bits.value == 0
    assert dut.uio_out.value[1:0] == 0
#    assert dut.user_project.serial2parallel_data.value == 0

    helpers.decoder_buffer = []
    data = [1] * 12 + [0] * 14 + [1] * 6
    await helpers.manchester_encode(data, speed=19, pin=0)
    assert helpers.decoder_buffer == data
#    assert dut.user_project.counters_bits.value == 0
    assert dut.uio_out.value[1:0] == 3
    assert dut.uio_out.value[3] == 0
    assert dut.uo_out.value[7] == 1  # PWM_SET
#    assert dut.user_project.serial2parallel_data.value == 0
    assert dut.uio_out.value[4] == 0  # manchester encoder error

    for wait in range(0, 50):
        await helpers.n_clock(1)
        helpers.log_outputs()
    assert dut.uio_out.value[4] == 0  # manchester encoder error
    assert dut.uio_out.value[5] == 0  # frame
    assert dut.uo_out.value[7] == 0  # PWM_SET
#    assert dut.user_project.serial2parallel_data.value[9:0] == 0x3FF
#    assert dut.user_project.serial2parallel_data.value[19:10] == 1
#    assert dut.user_project.serial2parallel_data.value[29:20] == 0x3E0

    for wait in range(0, 4096):
        await helpers.n_clock(1)
        helpers.log_outputs()
        helpers.pwm_decode()

    # TODO. Green should be in the middle and all should be twice as fast.
    assert helpers.led_green == 2
    assert helpers.led_blue == 0x3E0 * 2
    assert helpers.led_red == 0x3FF * 2
