from z3 import And, Int
from itertools import permutations
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped, ks


class Thermometer(Ruleset):

    def register(self):
        return "Thermometer", "Enter thermometer, in ascending order from 1 to (max) 9", -1

    def to_sat(self, layer):
        steps = self.get_steps(layer)

        possible = [p for p in permutations(ks, len(steps)) if p == tuple(sorted(p))]
        return grouped(or_clause([grouped(and_clause([f"{steps[i]}{p[i]}" for i in range(len(p))])) for p in possible]))

    def to_smt(self, layer):
        steps = self.get_steps(layer)
        s = [Int(st) for st in steps]
        return [And(*[s[i] > s[i-1] for i in range(1, len(s))])]

    def get_steps(self, layer):
        if len(layer.replace(".", "")) < 2:
            return None
        steps = [(int(layer[i]), f"S{i // 9 + 1}{i % 9+ 1}") for i in range(81) if layer[i] in "123456789"]
        steps.sort(key=lambda t: t[0])
        steps = [x[1] for x in steps]
        return steps

    def random_rule(self):
        thermo = list(range(1, self.randint(3, 6)))
        if self.randint(0, 1) == 1:
            thermo.reverse()

        return thermo

    def to_html(self, layer):
        first = next((i for i in range(81) if layer[i] != "."), -1)
        if first < -1:
            return super().to_html()

        if self.is_horizontal(layer):
            return [f'<div class="thermometer horizontal len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]

        else:
            return [f'<div class="thermometer vertical len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]
