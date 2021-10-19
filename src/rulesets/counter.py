from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped


class Thermometer(Ruleset):

    def register(self):
        return "Counter", "Enter counter, in ascending order from 1 to (max) 9", -1

    def to_sat(self, layer):
        if len(layer.replace(".", "")) < 2:
            return None
        steps = [(int(layer[i]), f"S{i // 9 + 1}{i % 9+ 1}") for i in range(81) if layer[i] in "123456789"]
        steps.sort(key=lambda t: t[0])
        steps = [x[1] for x in steps]

        sliding_window = len(steps)

        variants = []
        for i in range(9 - sliding_window + 1):
            variants.append(grouped(and_clause([s + str(steps.index(s) + i + 1) for s in steps])))

        return grouped(or_clause(variants))
