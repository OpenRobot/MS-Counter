class Hexadecimal:
    def __init__(self, db):
        self.db = db

    def encode(self, num):
        return hex(int(num))[2:]

    def decode(self, num):
        return int(str(num), base=16)
