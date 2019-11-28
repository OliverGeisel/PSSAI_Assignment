from os import path


class Decoder:

    def __init__(self, file : path):
        with file as data:
            self.data = data

    def parse(self):
        pass
