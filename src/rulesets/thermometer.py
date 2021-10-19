from itertools import permutations
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped, ks


class Thermometer(Ruleset):

    def register(self):
        return "Thermometer", "Enter thermometer, in ascending order from 1 to (max) 9", -1

    def to_sat(self, layer):
        if len(layer.replace(".", "")) < 2:
            return None
        steps = [(int(layer[i]), f"S{i // 9 + 1}{i % 9+ 1}") for i in range(81) if layer[i] in "123456789"]
        steps.sort(key=lambda t: t[0])
        steps = [x[1] for x in steps]

        possible = [p for p in permutations(ks, len(steps)) if p == tuple(sorted(p))]
        return grouped(or_clause([grouped(and_clause([f"{steps[i]}{p[i]}" for i in range(len(p))])) for p in possible]))


def generate_new(max=4):
    from random import randint, shuffle

    lines = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    shuffle(lines)
    for line in lines[0:randint(0, max)]:
        rule = create_new()

        before_pad = [0 for i in range(randint(0, 9 - len(rule)))]
        after_pad = [0 for i in range(9 - len(rule) - len(before_pad))]
        rule = before_pad + rule + after_pad

        if randint(0, 1) == 0:
            yield to_row(rule, line)
        else:
            yield to_col(rule, line)


def to_row(rule, row):
    str_row = "".join([str(x) if x != 0 else "." for x in rule])
    return "........." * row + str_row + "........." * (8 - row)


def to_col(rule, col):
    str_col = "".join([str(x) if x != 0 else "." for x in rule])
    return "".join(["." * col + str_col[i] + "." * (8 - col) for i in range(9)])


def create_new():
    from random import randint

    thermo = list(range(1, randint(3, 6)))
    if randint(0, 1) == 1:
        thermo.reverse()

    return thermo


print("\n".join("".join([str(i) for i in x]) for x in generate_new()))
