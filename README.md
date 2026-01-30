![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Architecture

The architecture of the digital LED is based on a pipelined signal flow. The following modules are used

1) Input Signal
2) Low pass filter
3) Manchester decoder
4) Frame Detector Insync
5) Bit and word counters
6) Parity Detection
7) Selector
8) Pulse Width Modulator
9) Manchester encoder

## 1. Input Selector
The first module is the "input_selector.v". At startup, is selects either the IN0 input or IN1 input based on whether Inß shows a toggling signal. The IN0 must toggle 63 times until the input is selected. This decision is only made once after reset. 
However, if the test-mode command is send, then the input is switched from IN0 to IN1 or vice versa regardless of the internal selection.
If IN1 has toggle 255 times, then the input selector does not select IN0 anymore but remains with it IN1 selection.
The algorithmic delay is one clock cylce

### Inputs and Outputs
* IN0 (i) Data signal input from previous LED
* IN1 (i) Data signal input from the penultimate LED 
* TEST_MODE (i) True if the test_mode selected.
* OUT (o) Data signal output (either from IN0 or IN1)
* IN0SELECTED (o) True, if IN0 is selected. It toggles with if test-mode is switched on. 

## Low pass filter
In order to avoid spikes, the low pass filter filters out spikes which have a length of one clock cycle, are removed.
The algorithmic delay is two clock cycles.

### Inputs and Outputs
* IN (i) Data signal input from input_selector's OUT
* OUT (o) Low-pass filtered data signal output

## 2. A Manchester decoder
The input signal is decoded according to the Manchester coding. Both the data signal and the clock signal are reconstructed. If the input signal looks strange or is missing , this is reported. We assume that the frequency of the input is about 24 times less than the internal clock signal. However, very data bit, the real length of the data is measured and reported.
The clock tolerance ranges from -25% faster to +50% slower than the one given by the clock frequency divided by 24.
The algorithmic delay is one clock cycle.
If the decoder is in error state, then a long impulse is needed to reset it to good. 

### Inputs and Outputs
* IN (i) Data signal input from low pass filters's OUT
* OUT_DATA (o) data signal bit. It is only valid while OUT_CLK is high, too.
* OUT_CLK (o) one cycle high indicating a new OUT_DATA 
* OUT_ERROR (o) the manchester decoding is not according to definition. It remain in error state till a good long bit is detected (e.g., a 10 bit sequences) 
* OUT_PULSEWIDTH (o) the 6 bit length of the last bit. 

## 3. Synchronizing the beginning of a frame
Based on the output of the Manchester decoder, the frame start is detected. The first byte of a frame must start with two ones in row (two short pulses). Before that, alternating 1 or 0 are expected (long pulses).
It outputs a signal "insync" to indicate that the frame start has been detected and that the following data contains valid LED data.
The algorithmic delay is one cycle.

### Inputs and Outputs
* IN_DATA (i) the bit from the Manchester decodign.
* IN_CLK (i) the clock signal from the Manchester decoding 
* IN_ERROR (i) The manchester decoding is in error state
* INSYNC (o) Indicate whether the frame has started
* OUT_DATA (o) Valid data within a frame
* OUT_CLK (o) Valid clock within a frame

## 4. Counting the bits of LED data and the LEDs
The next modules counts bits of a LED data and the number of LEDs.
The bits are used to control the next stages. If the number of LEDs reaches 4095, then the test mode is switched on.
This block has an algorithmic delay of one clock cycle.

### Inputs and Output
* IN_DATA (i) Valid data within a frame from insync
* IN_CLK (i) Valid clock within a frame from insync
* INSYNC (i) if false, sets the counter back to zero, from the insync module 
* BIT_COUNTER (o) counting the 32 bits
* TEST_MODE (o) 4095 LEDs switches the test mode on.
* OUT_DATA (o) data within a frame delayed by one cycle
* OUT_CLK (o) clock within a frame delayed by one cycle

## 6. Calculating the parity of a word
It calculate the parity of the first 31 bits and compares it with the last bit.

### Inputs and Output
* IN_DATA (i) Valid data within a frame from insync
* IN_CLK (i) Valid clock within a frame from insync
* INSYNC (i) if false, sets the counter back to zero, from the insync module 
* BIT_COUNTER (i) counting the 32 bits
* TEST_MODE (o) 4095 LEDs switches the test mode on.
* ERROR (o) true if the last bit has a wrong parity

# Tiny Tapeout Verilog Project Template

- [Read the documentation for project](docs/info.md)

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Set up your Verilog project

1. Add your Verilog files to the `src` folder.
2. Edit the [info.yaml](info.yaml) and update information about your project, paying special attention to the `source_files` and `top_module` properties. If you are upgrading an existing Tiny Tapeout project, check out our [online info.yaml migration tool](https://tinytapeout.github.io/tt-yaml-upgrade-tool/).
3. Edit [docs/info.md](docs/info.md) and add a description of your project.
4. Adapt the testbench to your design. See [test/README.md](test/README.md) for more information.

The GitHub action will automatically build the ASIC files using [LibreLane](https://www.zerotoasiccourse.com/terminology/librelane/).

## Enable GitHub actions to build the results page

- [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
  - Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)

# Notes

iverilog -o sim_build/gl/sim.vvp -s tb -g2012 -DGL_TEST -DFUNCTIONAL -DSIM -Isrc -f sim_build/gl/cmds.f lsihp-sg13g2/libs.ref/sg13g2_io/verilog/sg13g2_io.v /home/runner/pdk/ihp-sg13g2/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v /home/runner/work/tt_um_hoene_firsttry/tt_um_hoene_firsttry/test/gate_level_netlist.v /home/runner/work/tt_um_hoene_firsttry/tt_um_hoene_firsttry/test/tb.v
