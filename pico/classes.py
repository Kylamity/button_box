# classes.py
# Author: Kyle Schack

import time
      
##--------------------------------------------------------------------------------------------------------------------------
class ModeHandler:
    def __init__(self, mode_switch_pins: list[object]):
        self.current_mode = 0
        self.mode_switch = ToggleSwitch(mode_switch_pins)
        
    def read_switch(self):
        self.mode_switch.read_position()
        if self.mode_switch.position != self.current_mode:
            self.current_mode = self.mode_switch.position
        
##--------------------------------------------------------------------------------------------------------------------------     
class GamepadHandler:
    def __init__(self, gamepad: object):
        self.gamepad = gamepad
        self.input_values: list[bool] = []
        self.sent_values: list[bool] = []
        self.flagged_values: list[int] = [] # index number of values that fail compare
        
    def update(self, input_values: list[bool]):
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
    def __init__(self, neopixels: list[object], default_color: str = 'white', default_brightness: float = 0.5):
        self.neopixels = neopixels
        self.color = default_color
        self.brightness = default_brightness
        self.rgb_colors = self.rgb_color_dict()
        self.status_color = 'green'
        self.blink_timestamp = time.time()
        self.blink_enabled = False
        self.blink_state = False
        self.init_neopixels()
        
    def run(self):
        self.blink()
        
    def init_neopixels(self):
        self.neopixels.brightness = self.brightness
        self.neopixels.fill(self.rgb_colors[self.color])
        self.set_color(0, self.status_color)
        
    def set_color(self, led_number: int, color: str):
        self.neopixels[led_number] = self.rgb_colors[color]
        self.neopixels.show()
        
    def blink(self):
        if self.blink_enabled:
            current_time = time.time()
            elapsed_time = current_time - self.blink_timestamp
            if elapsed_time >= 1:
                if self.blink_state:
                    self.set_color(0, 'off')
                    self.blink_state = False
                else:
                    self.set_color(0, self.status_color)
                    self.blink_state = True
                self.blink_timestamp = current_time
        elif not self.blink_enabled and not self.blink_state:
            self.blink_state = True
            self.set_color(0, self.status_color)
            
    def set_status_color(self, color: str):
        if self.status_color != color:
            self.status_color = color
            self.set_color(0, color)
    
    def rgb_color_dict(self):
        return {
            'red':    (255, 0, 0),
            'green':  (0, 255, 0),
            'blue':   (0, 0, 255),
            'white':  (255, 255, 255),
            'yellow': (255, 255, 0),
            'purple': (255, 0, 255),
            'cyan':   (0, 255, 255),
            'off':    (0, 0, 0),
        }

##--------------------------------------------------------------------------------------------------------------------------
##--------------------------------------------------------------------------------------------------------------------------
class PISOShiftRegisters:
    def __init__(self, pin_sda: object, pin_ld: object, pin_sck: object, num_bits: int):
        self.pin_sda = pin_sda # gpio pin
        self.pin_ld = pin_ld # gpio pin
        self.pin_sck = pin_sck # gpio pin
        self.num_bits = num_bits # total number of bits in register cascade
        self.bit_states: list[bool] = []
        self.init_states_list
        self.init_pins()
        
    def init_states_list(self):
        for i in range(len(self.num_bits)):
            self.bit_states.append(False)

    def init_pins(self):
        self.pin_sck.value = False
        self.pin_ld.value = False

    def read_bits(self):
        bit_states = []
        self.pin_ld.value = True
        for bit in range(self.num_bits):
            bit_states.append(self.pin_sda.value)
            self.pin_sck.value = True
            time.sleep(0.001) # 1ms bit shift delay
            self.pin_sck.value = False
        self.pin_ld.value = False
        self.bit_states = bit_states
        
##--------------------------------------------------------------------------------------------------------------------------
class ToggleSwitch:
    def __init__(self, input_pins: list[object]):
        self.input_pins = input_pins # list index 0 = switch position 1
        self.position = 0
        
    def read_position(self):
        for i in range(len(self.input_pins)):
            if self.input_pins[i].value is True:
                self.position = i + 1
                return None
        self.position = 0
        
        