class Roman:
    def __init__(self, db):
        roman = dict()
        roman[100000] = "C̅"
        roman[90000] = "X̅C̅"
        roman[50000] = "L̅"
        roman[40000] = "X̅L̅"
        roman[10000] = "X̅"
        roman[9000] = "MX̅"
        roman[5000] = "V̅"
        roman[1000] = "M"
        roman[900] = "CM"
        roman[500] = "D"
        roman[400] = "CD"
        roman[100] = "C"
        roman[90] = "XC"
        roman[50] = "L"
        roman[40] = "XL"
        roman[10] = "X"
        roman[9] = "IX"
        roman[5] = "V"
        roman[4] = "IV"
        roman[1] = "I"

        self.roman = roman

        self.switched_roman = dict([(v, k) for k, v in self.roman.items()])

        self.db = db

    def encode(self, num) -> str:
        def roman_num(num):
            for r in self.roman.keys():
                x, y = divmod(num, r)
                yield self.roman[r] * x
                num -= (r * x)
                if num <= 0:
                    break

        return "".join([a for a in roman_num(num)])

    def decode(self, roman) -> int:
        roman = str(roman).upper()

        values = [self.switched_roman[r] for r in roman]
        return int(sum(
            val if val >= next_val else -val
            for val, next_val in zip(values[:-1], values[1:])
        ) + values[-1])