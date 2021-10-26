from z3 import Int
from itertools import permutations
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped, ks


class AreaSums(Ruleset):

    def register(self):
        return "AreaSums", "Allowed: from C=3 up to Q=17. Mark exactly two adjacent fields w/ same letter.", -1

    def to_sat(self, layer):
        areas = {}
        for i in range(81):
            if layer[i] in "CDEFGHIJKLMNOPQ":
                areas.setdefault(ord(layer[i]) - 64, []).append(f"S{i // 9 + 1}{i % 9+ 1}")

        rules = []
        for value, fields in areas.items():
            if len(fields) == 2:
                rules.append(self.generate_for_area(value, fields))
        return grouped(and_clause(rules))

    def to_smt(self, layer):
        areas = {}
        for i in range(81):
            if layer[i] in "CDEFGHIJKLMNOPQ":
                areas.setdefault(ord(layer[i]) - 64, []).append(f"S{i // 9 + 1}{i % 9+ 1}")

        rules = []
        for value, fields in areas.items():
            if len(fields) == 2:
                rules.append(Int(fields[0]) + Int(fields[1]) == value)
        return rules

    @staticmethod
    def generate_for_area(value, fields):
        summands = [(i, j) for i, j in permutations(ks, 2) if i != j and i + j == value]
        return grouped(or_clause([f"({fields[0]}{i} & {fields[1]}{j})" for i, j in summands]))

    def random_rule(self):
        return list("CDEFGHIJKLMNOPQ"[self.randint(0, 14)]*2)

    def to_html(self, layer):
        first = next((i for i in range(81) if layer[i] != "."), -1)
        if first < -1:
            return super().to_html()

        sum_value = ord(layer[first]) - 64

        if self.is_horizontal(layer):
            return [f'<div class="areasum horizontal">{sum_value}</div>' if i == first else "" for i in range(81)]

        else:
            return [f'<div class="areasum vertical">{sum_value}</div>' if i == first else "" for i in range(81)]
