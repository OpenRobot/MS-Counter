class Hexadecimal:
    def __init__(self, db):
        self.db = db

    def encode(self, num):
        return str(hex(int(num)))

    def decode(self, num):
        return int(str(num), base=16)
