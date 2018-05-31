PLAY_BUTTON = 24
RECORD_BUTTON = 25
import keyboard 

class GPIO:
    BCM = 0
    IN = 0
    
    @staticmethod
    def setmode(mode):
        print("Mode: {}".format(mode))
        
    @staticmethod
    def setup(pin, direction):
        print("Set Pin: {} to {}".format(pin, direction))
        
    @staticmethod
    def input(pin):        
        if pin == PLAY_BUTTON:
            return keyboard.is_pressed('p')
        elif pin == RECORD_BUTTON:
            return keyboard.is_pressed('r')
        else:
            return false
        
    @staticmethod
    def cleanup():
        print("GPIO Cleanup")
