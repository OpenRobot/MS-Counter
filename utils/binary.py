class Binary:
    def __init__(self, db):
        self.db = db

    def encode(self, num) -> int:
        return int(bin(num)[2:])

    def decode(self, num) -> int:
        return int(str(num), base=2)