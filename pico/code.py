# code.py (main)
# Author: Kyle Schack

##---------------------------------------------------------------------------Dependency imports
import board, digitalio, neopixel, usb_hid, time
from hid_gamepad import Gamepad
from classes import *

##---------------------------------------------------------------------------Configuration
NUM_INPUT_BITS = 0 # total bits in PISO shift register cascade
NUM_INPUT_BITS_BUILTIN = 16 # total always connected (built in) PISO shift register bits
#NUM_OUTPUT_BITS = 8 # total bits in SIPO shift register cascade
NUM_NEOPIXELS = 0 # total neopixels in external chain
NUM_NEOPIXELS_BUILTIN = 1 # total always connected (built in) neopixels
NEOPIXEL_GROUP_SIZE = 5
NEOPIXEL_COLOR = 'blue' # default color
NEOPIXEL_BRIGHTNESS = 0.1 # default brightness (range 0 - 1)
WHEEL_POWER_BUTTONS = [12, 14] # numbers to be offset by -1 to address bit index (needs fixed)

##---------------------------------------------------------------------------Object Definitions
## GPIO Pins
pin_sda_in: object = digitalio.DigitalInOut(board.GP0)
pin_ld: object = digitalio.DigitalInOut(board.GP1)
#pin_sda_out: object = digitalio.DigitalInOut(board.GP2)
#pin_lt: object = digitalio.DigitalInOut(board.GP3)
pin_sck: object = digitalio.DigitalInOut(board.GP4)
pin_mode_1: object = digitalio.DigitalInOut(board.GP16)
pin_mode_2: object = digitalio.DigitalInOut(board.GP17)
#pin_dd_enable: object = digitalio.DigitalInOut(board.GP27)
pin_sda_neopixel: object = board.GP28

# Pin directions
pin_sda_in.direction = digitalio.Direction.INPUT
pin_ld.direction = digitalio.Direction.OUTPUT
#pin_sda_out.direction = digitalio.Direction.OUTPUT
#pin_lt.direction = digitalio.Direction.OUTPUT
pin_sck.direction = digitalio.Direction.OUTPUT
pin_mode_1.direction = digitalio.Direction.INPUT
pin_mode_2.direction = digitalio.Direction.INPUT
#pin_dd_enable.direction = digitalio.Direction.OUTPUT

## Other
inputs: object = PISOShiftRegisters(pin_sda_in, pin_ld, pin_sck, NUM_INPUT_BITS + NUM_INPUT_BITS_BUILTIN)
#outputs: object = SIPOShiftRegisters(pin_sda_out, pin_lt, pin_sck, NUM_OUTPUT_BITS)
mode_handler = ModeHandler([pin_mode_1, pin_mode_2])
gamepad: object = Gamepad(usb_hid.devices)
gamepad_handler: object = GamepadHandler(gamepad)
neopixels: list[object] = neopixel.NeoPixel(pin_sda_neopixel, NUM_NEOPIXELS + NUM_NEOPIXELS_BUILTIN)
neopixel_handler: object = NeopixelHandler(neopixels, NEOPIXEL_COLOR, NEOPIXEL_BRIGHTNESS)


##---------------------------------------------------------------------------Logic
def main():
    wheel_power_enabled = False
    
    while True:
        neopixel_handler.run()
        mode_handler.read_switch()
        inputs.read_bits()
        
        mode = mode_handler.current_mode

        if mode is 0 or mode is 1:
            neopixel_handler.set_status_color('green')
            gamepad_handler.update(inputs.bit_states)
            
        elif mode is 2:
            neopixel_handler.set_status_color('yellow')
                 

main()