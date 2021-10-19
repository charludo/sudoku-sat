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

    def random_rule(self):
        thermo = list(range(1, self.randint(3, 6)))
        if self.randint(0, 1) == 1:
            thermo.reverse()

        return thermo
