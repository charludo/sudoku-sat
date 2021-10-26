from z3 import And, Int
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped


class Counter(Ruleset):

    def register(self):
        return "Counter", "Enter counter, in ascending order from 1 to (max) 9", -1

    def to_sat(self, layer):
        steps = self.get_steps(layer)

        sliding_window = len(steps)

        variants = []
        for i in range(9 - sliding_window + 1):
            variants.append(grouped(and_clause([s + str(steps.index(s) + i + 1) for s in steps])))

        return grouped(or_clause(variants))

    def to_smt(self, layer):
        steps = self.get_steps(layer)
        s = [Int(st) for st in steps]
        return [And(*[s[i] == s[i-1] + 1 for i in range(1, len(s))])]

    def get_steps(self, layer):
        if len(layer.replace(".", "")) < 2:
            return None
        steps = [(int(layer[i]), f"S{i // 9 + 1}{i % 9+ 1}") for i in range(81) if layer[i] in "123456789"]
        steps.sort(key=lambda t: t[0])
        steps = [x[1] for x in steps]
        return steps

    def random_rule(self):
        counter = list(range(1, self.randint(3, 6)))
        if self.randint(0, 1) == 1:
            counter.reverse()

        return counter

    def to_html(self, layer):
        first = next((i for i in range(81) if layer[i] != "."), -1)
        if first < -1:
            return super().to_html()

        if self.is_horizontal(layer):
            return [f'<div class="counter horizontal len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]

        else:
            return [f'<div class="counter vertical len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]
