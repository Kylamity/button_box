# code.py (main)
# Author: Kyle Schack

##---------------------------------------------------------------------------Dependency imports
import board, digitalio, neopixel, usb_hid, time
from hid_gamepad import Gamepad
from classes import *

##---------------------------------------------------------------------------Configuration
NUM_INPUT_BITS = 0 # total bits in PISO shift register cascade
NUM_INPUT_BITS_BUILTIN = 16 # total always connected (built in) PISO shift register bits
NUM_OUTPUT_BITS = 8 # total bits in SIPO shift register cascade
NUM_NEOPIXELS = 0 # total neopixels in external chain
NUM_NEOPIXELS_BUILTIN = 1 # total always connected (built in) neopixels
NEOPIXEL_GROUP_SIZE = 5
NEOPIXEL_COLOR = 'green' # default color
NEOPIXEL_BRIGHTNESS = 0.05 # default brightness (range 0 - 1)
WHEEL_POWER_BUTTONS = [12, 14, 13, 15] # [on, on, off, off] numbers to be offset by -1 to address bit index (needs fixed)

##---------------------------------------------------------------------------Object Definitions
## GPIO Pins
pin_sda_in: object = digitalio.DigitalInOut(board.GP0)
pin_ld: object = digitalio.DigitalInOut(board.GP1)
pin_sda_out: object = digitalio.DigitalInOut(board.GP2)
pin_lt: object = digitalio.DigitalInOut(board.GP3)
pin_sck: object = digitalio.DigitalInOut(board.GP4)
pin_mode_1: object = digitalio.DigitalInOut(board.GP16)
pin_mode_2: object = digitalio.DigitalInOut(board.GP17)
pin_sda_neopixel: object = board.GP28

## PIN DIRECTIONS
pin_sda_in.direction = digitalio.Direction.INPUT
pin_ld.direction = digitalio.Direction.OUTPUT
pin_sda_out.direction = digitalio.Direction.OUTPUT
pin_lt.direction = digitalio.Direction.OUTPUT
pin_sck.direction = digitalio.Direction.OUTPUT
pin_mode_1.direction = digitalio.Direction.INPUT
pin_mode_2.direction = digitalio.Direction.INPUT

## Other
inputs: object = PISOShiftRegisters(pin_sda_in, pin_ld, pin_sck, NUM_INPUT_BITS + NUM_INPUT_BITS_BUILTIN)
outputs: object = SIPOShiftRegisters(pin_sda_out, pin_lt, pin_sck, NUM_OUTPUT_BITS)
gamepad: object = Gamepad(usb_hid.devices)
gamepad_handler: object = GamepadHandler(gamepad)
neopixels: list[object] = neopixel.NeoPixel(pin_sda_neopixel, NUM_NEOPIXELS + NUM_NEOPIXELS_BUILTIN)
neopixel_handler: object = NeopixelHandler(neopixels, NEOPIXEL_COLOR, NEOPIXEL_BRIGHTNESS)
powerSwitcher: object = PowerSwitcher(WHEEL_POWER_BUTTONS)

##---------------------------------------------------------------------------Logic
sysMode = 0

def sysModeUpdate():
    global sysMode
    if not pin_mode_1.value and not pin_mode_2.value and not sysMode == 0:
        if powerSwitcher.wheelPowerTimestamp:
            powerSwitcher.wheelPowerTimestamp = 0
        neopixel_handler.set_status_color(NEOPIXEL_COLOR)
        sysMode = 0
            
    elif pin_mode_1.value and not sysMode == 1:
        if powerSwitcher.wheelPowerTimestamp:
            powerSwitcher.wheelPowerTimestamp = 0
        neopixel_handler.set_status_color(NEOPIXEL_COLOR)
        sysMode = 1
        
    elif pin_mode_2.value and not sysMode == 2:
        neopixel_handler.set_status_color('yellow')
        sysMode = 2
    

def handleAction(action):
    if action == 'wheel on':
        outputs.bitStates[0] = True
    elif action == 'wheel off':
        outputs.bitStates[0] = False
    elif action == 'monitors on':
        outputs.bitStates[1] = True
    elif action == 'monitors off':
        outputs.bitStates[1] = False
    
    
def main():
    while True:
        sysModeUpdate()
        inputs.read()
        outputs.write()
        neopixel_handler.run()
        if sysMode is 0 or sysMode is 1:
            gamepad_handler.run(inputs.bit_states)
        elif sysMode is 2:
            action = powerSwitcher.userAction(inputs.bit_states)
            if action:
                handleAction(action)
                

main()