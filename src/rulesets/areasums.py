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

    @staticmethod
    def generate_for_area(value, fields):
        summands = [(i, j) for i, j in permutations(ks, 2) if i != j and i + j == value]
        return grouped(or_clause([f"({fields[0]}{i} & {fields[1]}{j})" for i, j in summands]))
