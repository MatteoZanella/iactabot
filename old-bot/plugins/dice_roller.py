import random
from lark import Transformer


def roll(num_of_dice: int, num_of_faces: int):
    return [random.randint(1, num_of_faces) for _ in range(num_of_dice)]


grammar = '''
    ?start: sum
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub
    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
    ?atom: "(" sum ")" -> parenthesis
        | dice [LABEL QUANTITY] -> selector
        | MODIFIER
    dice: [QUANTITY] "d" FACES
    
    MODIFIER: "0" | "1".."9" [INT]
    QUANTITY: "1".."9" [INT]
    FACES:  "1".."9" INT | "2".."9"
    LABEL: ("d" | "k") ["h" | "l"]
    
    %import common.INT
    %import common.WS
    %ignore WS
'''


class MyTransformer(Transformer):
    def add(self, items: list):
        return items[0][0] + items[1][0], items[0][1] + ' + ' + items[1][1]

    def sub(self, items: list):
        return items[0][0] - items[1][0], items[0][1] + ' - ' + items[1][1]

    def mul(self, items: list):
        return items[0][0] * items[1][0], items[0][1] + ' * ' + items[1][1]

    def div(self, items: list):
        return items[0][0] // items[1][0], items[0][1] + ' / ' + items[1][1]

    def parenthesis(self, items: list):
        return items[0][0], '( ' + items[0][1] + ' )'

    def dice(self, items: list):
        if len(items) == 1:
            return roll(1, items[0])
        else:
            return roll(items[0], items[1])

    def selector(self, items: list):
        rolls = items[0]
        if len(items) == 1 or (items[1][0] == 'k' and items[2] >= len(items[0])):
            return sum(rolls), str(rolls)
        elif items[1][0] == 'd' and items[2] >= len(items[0]):
            return 0, '[~~' + '~~, ~~'.join(str(x) for x in rolls) + '~~]'
        else:
            label, quantity = items[1], items[2]
            rolls.sort(reverse=True)
            if label[1] == 'l':
                quantity = -quantity
            if label == 'kh' or label == 'dl':
                summary = '[' + ', '.join(str(x) for x in rolls[:quantity]) \
                          + ', ~~' + '~~, ~~'.join(str(x) for x in rolls[quantity:]) + '~~]'
                return sum(rolls[:quantity]), summary
            else:
                summary = '[~~' + '~~, ~~'.join(str(x) for x in rolls[:quantity]) + '~~, ' \
                          + ', '.join(str(x) for x in rolls[quantity:]) + ']'
                return sum(rolls[quantity:]), summary

    def MODIFIER(self, val):
        return int(val), str(val)

    def QUANTITY(self, val):
        return int(val)

    def FACES(self, val):
        return int(val)

    def LABEL(self, val: str):
        if val == 'k':
            return 'kh'
        elif val == 'd':
            return 'dl'
        else:
            return val
