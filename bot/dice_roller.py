import random
from lark import Transformer, Lark, ParseError, UnexpectedInput
from lark.exceptions import VisitError
from constants import MAX_QUERY_LENGTH, MAX_SUMMARY_LENGTH


def roll_query(query: str) -> str:
    try:
        if len(query) > MAX_QUERY_LENGTH:
            raise TimeoutError
        syntax_tree = Lark(grammar).parse(query)
        result, summary = RollTransformer().transform(syntax_tree)
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:MAX_SUMMARY_LENGTH] + "..."
        return f"*{result}*  \\=  {summary}"
    except (UnexpectedInput, AttributeError, ParseError):
        return "I can't roll this. Have you tried the /help command? 🤔"
    except TimeoutError:
        return "Too difficult to calculate 😩"
    except VisitError:
        return "Impossible to divide by zero 😒"


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


def roll_dice(num_of_dice: int, num_of_faces: int):
    return [random.randint(1, num_of_faces) for _ in range(num_of_dice)]


class RollTransformer(Transformer):

    @staticmethod
    def add(items: list):
        return items[0][0] + items[1][0], items[0][1] + ' \\+ ' + items[1][1]

    @staticmethod
    def sub(items: list):
        return items[0][0] - items[1][0], items[0][1] + ' \\- ' + items[1][1]

    @staticmethod
    def mul(items: list):
        return items[0][0] * items[1][0], items[0][1] + ' \\* ' + items[1][1]

    @staticmethod
    def div(items: list):
        return items[0][0] // items[1][0], items[0][1] + ' / ' + items[1][1]

    @staticmethod
    def parenthesis(items: list):
        return items[0][0], '\\( ' + items[0][1] + ' \\)'

    @staticmethod
    def dice(items: list):
        quantity, dice = items
        quantity = 1 if quantity is None else quantity
        return roll_dice(quantity, dice)

    @staticmethod
    def selector(items: list):
        rolls, label, quantity = items
        if label is None or (label[0] == 'k' and quantity >= len(rolls)):
            return sum(rolls), f"\\[{', '.join(map(str, rolls))}\\]"
        elif label[0] == 'd' and quantity >= len(rolls):
            return 0, f"\\[~{'~, ~'.join(map(str, rolls))}~\\]"
        else:
            rolls.sort(reverse=True)
            if label[1] == 'l':
                quantity = -quantity
            if label == 'kh' or label == 'dl':
                summary = f"\\[{', '.join(map(str, rolls[:quantity]))}, ~{'~, ~'.join(map(str, rolls[quantity:]))}~\\]"
                return sum(rolls[:quantity]), summary
            else:
                summary = f"\\[~{'~, ~'.join(map(str, rolls[:quantity]))}~, {', '.join(map(str, rolls[quantity:]))}\\]"
                return sum(rolls[quantity:]), summary

    @staticmethod
    def MODIFIER(val):
        return int(val), str(val)

    @staticmethod
    def QUANTITY(val):
        return int(val)

    @staticmethod
    def FACES(val):
        return int(val)

    @staticmethod
    def LABEL(val: str):
        if val == 'k':
            return 'kh'
        elif val == 'd':
            return 'dl'
        else:
            return val
