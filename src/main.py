import features
import json

class Crawler():
    def __init__(self):
        #dict for all input/output
        self.features = {}
        self.value_getter = self.get_one()

    def add_feature(self, this):
        self.features.update(this)

    def set(self, feature, value):
        self.features[feature].set(value)

    def get_one(self):
        while True:
            for feature, value in self.features.items():
                yield f"{feature} {value.get()}"

    def status_updater(self):
        self.run = True
        while self.run:
            print(next(self.value_getter))

    def stop(self):
        self.t.cancel()
        
c = Crawler()

#setup servos
for name, gpio, timeout in [("spd", 1, 2),("dir", 2, None),("pitch", 3, None),("yaw", 4, None)]:
    c.add_feature({name:features.Servo(gpio, timeout)})

def run():
    while True:
        try:
            feature, value = input().split()
            c.set(feature ,value)
        except ValueError:
            pass
        print(next(c.value_getter))
