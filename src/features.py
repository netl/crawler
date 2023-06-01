from machine import Pin

class Servo():
    def __init__(self, channel, timeout = None):
        #self.pwm = PWM( Pin(channel, Pin.OUT), freq=50, duty_ns=1.5e9) #50 hz, 1.5 ms pulse
        self.position = 0
        self.timeout = timeout

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set(self, pos):
        # pos: -1 ... 1 -> 1-2 ms pulse
        self.position = max(-1, min( 1, float(pos)))
        #self.pwm(1.5e9+self.position*0.5e9)

    def get(self):
        return self.position

def Analog_input():
    def __init__(self, channel):
        self.p = ADC(Pin(channel))

    def set(self, value):
        pass

    def get(self):
        return self.p.read_u16()/65536
        
def Digital_output():
    def __init__(self, channel):
        self.p = Pin(channel, Pin.OUT)

    def set(self, value):
        self.p.value(value)

    def get(self):
        return self.p.value()

def Digital_input():
    def __init__(self, channel):
        self.p = Pin(channel, Pin.IN)

    def set(self, value):
        if value:
            self.p.pull(Pin.PULL_UP)
        else:
            self.p.pull(Pin.PULL_DOWN)

    def get(self):
        return self.p.value()
