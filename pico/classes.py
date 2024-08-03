# classes.py
# Author: Kyle Schack

import time

class PowerSwitcher:
    def __init__(self, wheelPowerButtons: list):
        self.wheelPowerButtons = wheelPowerButtons
        self.wheelPowerTimestamp = 0
        
    def userAction(self, inputs: list):
        pressDelay = 5 #sec
        currentTime = time.time()
        if inputs[self.wheelPowerButtons[0]] and inputs[self.wheelPowerButtons[1]]:
            if self.wheelPowerTimestamp:
                if self.wheelPowerTimestamp <= currentTime - pressDelay:
                    self.wheelPowerTimestamp = 0
                    return 'wheel on'
                else:
                    return None
            else:
                self.wheelPowerTimestamp = currentTime
        else:
            self.wheelPowerTimestamp  = 0

##--------------------------------------------------------------------------------------------------------------------------     
class GamepadHandler:
    def __init__(self, gamepad: object):
        self.gamepad = gamepad
        self.input_values: list[bool] = []
        self.sent_values: list[bool] = []
        self.flagged_values: list[int] = [] # index number of values that fail compare
        
    def run(self, input_values: list[bool]):
        self.input_values = input_values
        if not self.compare_values():
            self.send_input_values()
        
    def compare_values(self):
        flagged_values = []
        if self.input_values != self.sent_values:
            try:
                for i in range(len(self.input_values)):
                    if self.input_values[i] != self.sent_values[i]:
                        flagged_values.append(i)
            except IndexError:
                for i in range(len(self.input_values)):
                    self.sent_values.append(i)
                    self.sent_values[i] = self.input_values[i]
            if flagged_values:
                self.flagged_values = flagged_values
                return False
        return True
            
    def send_input_values(self):
        for i in range(len(self.flagged_values)):
            flagged_value_index = self.flagged_values[i]
            button_number = (flagged_value_index + 1)
            if self.input_values[flagged_value_index]:
                self.gamepad.press_buttons(button_number)
            else:
                self.gamepad.release_buttons(button_number)
            self.sent_values[flagged_value_index] = self.input_values[flagged_value_index]

##--------------------------------------------------------------------------------------------------------------------------
class NeopixelHandler:
    def __init__(self, neopixels: list[object], default_color: str = 'none', default_brightness: float = 0.5):
        self.neopixels = neopixels
        self.color = default_color
        self.brightness = default_brightness
        self.rgb_colors: list[str] = self.rgb_color_dict()
        self.status_color = ''
        self.init_neopixels()
        
    def run(self):
        pass
        
    def init_neopixels(self):
        self.neopixels.brightness = self.brightness
        self.neopixels.fill(self.rgb_colors[self.color])
        
    def set_led_color(self, led_number: int, color: str):
        self.neopixels[led_number] = self.rgb_colors[color]
        #self.neopixels.show()
        
    def set_status_color(self, color: str):
        if self.status_color != color:
            self.set_led_color(0, color)
            self.status_color = color
            #self.neopixels.show()
    
    def rgb_color_dict(self):
        return {
            'red':    (255, 0, 0),
            'green':  (0, 255, 0),
            'blue':   (0, 0, 255),
            'white':  (255, 255, 255),
            'yellow': (255, 255, 0),
            'purple': (255, 0, 255),
            'cyan':   (0, 255, 255),
            'none':   (0, 0, 0)
        }
        
##--------------------------------------------------------------------------------------------------------------------------
class PISOShiftRegisters:
    def __init__(self, pin_sda: object, pin_ld: object, pin_sck: object, num_bits: int):
        self.pin_sda = pin_sda # gpio pin
        self.pin_ld = pin_ld # gpio pin
        self.pin_sck = pin_sck # gpio pin
        self.num_bits = num_bits # total number of bits in register cascade
        self.bit_states: list[bool] = []
        self.init_pins()
        
    def init_pins(self):
        self.pin_sck.value = False
        self.pin_ld.value = False
        
    def read(self):
        self.bit_states = []
        self.pin_ld.value = True
        for bit in range(self.num_bits):
            self.bit_states.append(self.pin_sda.value)
            self.pin_sck.value = True
            time.sleep(0.001) # 1ms bit shift delay
            self.pin_sck.value = False
        self.pin_ld.value = False
        
##--------------------------------------------------------------------------------------------------------------------------
class SIPOShiftRegisters:
    def __init__(self, pinSda: object, pinLT: object, pinSCK: object, numBits: int):
        self.pinSDA = pinSda
        self.pinLT = pinLT
        self.pinSCK = pinSCK
        self.numBits = numBits
        self.bitStates: list[bool] = []
        self.initPins()
        self.initBitStates()
        
    def initPins(self):
        self.pinSCK.value = False
        self.pinLT.value = True
        
    def initBitStates(self):
        for bit in range(self.numBits):
            self.bitStates.append(False)
    
    def write(self):
        self.pinLT.value = False
        for bit in range(self.numBits):
            self.pinSDA.value = self.bitStates[bit]
            self.pinSCK.value = True
            time.sleep(0.001) # 1ms bit shift delay
            self.pinSCK.value = False
        self.pinLT.value = True
    