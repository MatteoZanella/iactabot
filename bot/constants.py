MAX_QUERY_LENGTH = 100
MAX_SUMMARY_LENGTH = 500

START_TEXT = """
Hi, I'm IactaBot! I can roll any complex combination of dice.
You can also use me in any chat: just type @iactabot followed by a _dice formula_
"""
INSTRUCTIONS_TEXT = """
A _dice formula_ can contain combinations of:
• dice groups: `3d6`, `d20`
• numeric modifiers: `+2`, `-4`
• operations: `+`,`-`,`*`,`/`
• parenthesis: `(...)`
For each dice group you can also keep `k` or drop `d` the highest `h` or lowest `l` rolls.
For example, `4d6kl2` will keep the 2 lowest rolls and `4d6dh2` will drop the 3 highest rolls.
Using only `k` is equivalent to `kh`, while `d` is equivalent to `dl`.
"""
RICKROLL_TEXT = """
[Did you mean...?](http://www.youtube.com/watch?v=oHg5SJYRHA0)
"""