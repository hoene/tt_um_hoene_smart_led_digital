![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Smart LED Digital Design

This repository contains a chip design for Smart LEDs. It is based on the [Tiny Tapeout Verilog Project Template](docs/info.md)

# Architecture

The architecture of the digital LED is based on a pipelined signal flow. The following modules are used:

1) Input Selector
2) Low pass filter
3) Manchester decoder
4) Frame Detector
5) Bit and word counters
6) Selector
7) Parallel to Serial
8) Pulse Width Modulator
9) Manchester encoder

## 1. Input Selector
The first module is the "input_selector.v". At startup, is selects either the IN0 input or IN1 input based on whether IN0 shows a toggling signal. The IN0 input must toggle 63 times until this input is selected. After IN1 has toggled 255 times, the input selector does not select IN0 anymore but remains with it IN1 selection. These decisions are made only once after reset.
However, if the test-mode command is send, then the input is switched from IN0 to IN1 or vice versa regardless of the internal selection.
The algorithmic delay is one clock cycle.

### Inputs and Outputs
* IN0 (i,+0) Data signal input from previous LED
* IN1 (i,+0) Data signal input from the penultimate LED 
* TEST_MODE (i,+7) True if the test_mode selected.
* OUT (o,+1) Data signal output (either from IN0 or IN1)
* IN0SELECTED (o,+1) True, if IN0 is selected. It toggles if the test-mode is switched on.

## Low pass filter
In order to mitigate spikes and glitches in the input signals, a low pass filter filters out signals in which if 2 out of 5 bits are different.
The algorithmic delay is five clock cycles.

### Inputs and Outputs
* IN (i,+1) Data signal input from input_selector's OUT
* OUT (o,+5) Low-pass filtered data signal output

## 3. A Manchester decoder
The input signal is decoded according to the Manchester coding. Both the data signal and the clock signal are reconstructed. If the input signal looks strange or is missing, this is reported at OUT_ERROR. We assume that the frequency of the input is about 24 times less than the internal clock signal. However, for every data bit, the real length of the data is measured and reported.
The input signal might be 25% faster to 50% slower than the one given by the clock frequency divided by 24, while being considered valid.
The algorithmic delay is one clock cycle.
If the decoder is in error state, then a long impulse is needed to reset it to good. 

### Inputs and Outputs
* IN (i,+5) Data signal input from low pass filters's OUT
* OUT_DATA (o,+6) data signal bit. It is only valid while OUT_CLK is high, too.
* OUT_CLK (o,+6) one cycle high indicating a new OUT_DATA
* OUT_ERROR (o,+6) the manchester decoding is not according to definition. It remain in error state till a good long bit is detected (e.g., a one and zero bit sequences) 
* OUT_PULSEWIDTH (o,+6) the 6 bit length of the last bit. 

## 4. Synchronizing the beginning of a frame
Based on the output of the Manchester decoder, a frame start is detected. The first byte of a frame must start with two ones in row (two short pulses). Before that, alternating 1 or 0 are expected (which result in long pulses with Manchester encoding).
It outputs a signal "out_frame" to indicate that the frame start has been detected and that the following data contains valid LED data.
The algorithmic delay is one cycle.

### Inputs and Outputs
* IN_DATA (i,+6) the bit from the Manchester decoding
* IN_CLK (i,+6) the clock signal from the Manchester decoding
* IN_ERROR (i,+6) The manchester decoding is in error state
* OUT_FRAME (o,+7) True if the frame has started
* OUT_DATA (o,+7) IN_DATA delayed by one
* OUT_CLK (o,+7) IN_CLK delayed by one

## 5. Counting the bits of LED data and the number of LEDs
The next modules counts bits of a LED data word and the number of LED data words.
The bits are used to control the next stages. If the number of LEDs reaches 4095, then the test mode is switched on.
This block has an algorithmic delay of one clock cycle.

### Inputs and Output
* IN_DATA (i,+7) Input data
* IN_CLK (i,+7) Input clock
* IN_FRAME (i,+7) if true, the data is in a frame 
* BIT_COUNTER (o,+8) counting the 32 bits
* TEST_MODE (o,+8) 4095 LED data wordss switches the test mode on.
* OUT_DATA (o,+8) IN_DATA delayed by one
* OUT_CLK (o,+8) IN_CLK delayed by one
* OUT_FRAME (o,+8) IN_FRAME delayed by one

## 6. Select the right ând correct data for the LED
Based on the input modes, this modules selects the right LED data word which shall to be forwarded to the LED PWM.
It also modifies the input signal to mark used LEDs.
A LED data word has 32 bits: 
0: This bit indicates, whether the LED word shall be considered for display. The first (or second if in IN1 mode) data words are used. For those the bit is cleared. All preceeding and following data words are forwarded uneffected.
1-30: The three LED colors
31: Parity bit. It can be used to detect whether the parity is correct. It calculates the parity of the first 31 bits and compares it with the last bit.

### Inputs and Output
* IN_DATA (i+8) Valid data within a frame from counter
* IN_CLK (i+8) Valid clock within a frame from counter
* IN_FRAME (i+8) if true, the data is in a frame from counter
* IN0SELECTED (i+1) True, if IN0 is selected. It toggles with if test-mode is switched on. 
* BIT_COUNTER (i+8) counting the 32 bits
* PWM_SET (o+9) This data word shall be selected.
* OUT_DATA (o+9) The outgoing data signal, modified if required.
* OUT_CLK (o+9) IN_CLK delayed by one clock state.
* OUT_CLK_LED (o+9) Clock for the bit swift register
* ERROR (o) true if the protocol is violated.
* STATE (o) the internal state for testing purposes

## 8. Serial to Parallel
It contains a shift register to convert the serial input to a parallel 30 bit output and in addition a 30 bit register to store this output.

### Inputs and Output
* IN_DATA (i+9) Valid data within a frame from selector
* IN_CLK_LED (i+9) Valid clock within a frame from selector
* PWM_SET (i+9) If true, store data in output register
* OUTPUT_DATA (o+10) 30 bit output register

## 9. Pulse Width Modulator
Converts input bits to PWM outputs.

### Inputs and Output
* DATA_RED[9:0] (i+10) Brightness of red LED
* DATA_GREEN[9:0] (i+10) Brightness of green LED
* DATA_BLUE[9:0] (i+10) Brightness of blue LED
* OUT_RED (o) LED red on
* OUT_GREEN (o) LED green on
* OUT_BLUE (o) LED blue on

## 10. Manchester Encoder
Converts the outgoing data stream into a Manchester encoded signal.

### Inputs and Output
* IN_DATA (i,+10) Valid data within a frame from select
* IN_CLK (i,+10) Valid clock within a frame from select
* IN_PULSEWIDTH (i,+6) the 6 bit length of the last bit. 
* BIT_COUNTER (o,+8) counting the 32 bits
* DOUT (o) The 32 bit output register

# Overall Design

The Smart LED has the following input and output signals:

| port | pin | module | name | function |
| ---- | --- | ------ | ---- | -------- |
| in | 0 | input selector | IN0 | primary input data signal |
| in | 1 | input selector | IN1 | backup input data signal |
| in | 2-7 | - | - |
| out | 0 | input selector | IN0SELECTED | high if input 0 is selected |
| out | 1 | low pass filter | OUT | seelcted, low pass filtered signal |
| out | 2 | manchester decoder | data | the decoded data bit |
| out | 3 | manchester decoder | clk | the clock output |
| out | 4 | manchester decoder | error | error state |
| out | 5 | framing | frame | data frame detected |
| out | 6 | counters | test_mode | test mode active |
| out | 7 | protocol | PWM_SET | set the pwm generator |
| io | 1:0 | protocol | STATE | the current interal state |
| io 2 | protocol | ERROR | error in the protocol decoding |
| io 3 | protocol | OUT_DATA | data output  |
| io 4 | LED PWM | LED_RED | driving the red LED |
| io 5 | LED PWM | LED_GREEN | driving the green LED |
| io 6 | LED PWM | LED_BLUE | driving the blue LED |
| io 7 | Manchester encoder | OUT | output data signal |
