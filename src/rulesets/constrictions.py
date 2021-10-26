from z3 import Int, Or, And
from itertools import permutations, chain
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped, ks


class Constrictions(Ruleset):

    def register(self):
        return "Constrictions", "Upper/lower bounds: A-Z, constricted fields: a-z", -1

    def to_sat(self, layer):
        bounds, constricted = self.get_constrictions(layer)
        all_rules = []
        for letter, fields in bounds.items():
            if letter.lower() not in constricted or len(fields) != 2:
                continue

            letter_rules = []
            fields_lower = constricted[letter.lower()]
            bound_options = [(i, j) for i, j in permutations(ks, 2) if j - i > 1]

            for b1, b2 in bound_options:
                rule = f"(({fields[0]}{b1} & {fields[1]}{b2} | {fields[0]}{b2} & {fields[1]}{b1}) & "
                rule += and_clause([f"!{f}{k}" for k in chain(range(1, b1 + 1), range(b2, 10)) for f in fields_lower])
                rule += ")"

                # constriction_options = list(set([c for c in permutations(list(range(b1 + 1, b2))*len(fields_lower), len(fields_lower))]))

                # rule = f"(({fields[0]}{b1} & {fields[1]}{b2} | {fields[0]}{b2} & {fields[1]}{b1}) & "
                # rule += grouped(or_clause([grouped(and_clause([f"{fields_lower[i]}{c[i]}" for i in range(len(c))])) for c in constriction_options]))
                # rule += ")"

                letter_rules.append(rule)
            all_rules.append(grouped(or_clause(letter_rules)))
        return grouped(and_clause(all_rules))

    def to_smt(self, layer):
        bounds, constricted = self.get_constrictions(layer)
        all_rules = []
        for letter, fields in bounds.items():
            if letter.lower() not in constricted or len(fields) != 2:
                continue

            b1 = Int(fields[0])
            b2 = Int(fields[1])
            cons = [Int(c) for c in constricted[letter.lower()]]
            all_rules.append(Or(And(*[c > b1 for c in cons], *[c < b2 for c in cons]), And(*[c < b1 for c in cons], *[c > b2 for c in cons])))
        return all_rules

    def get_constrictions(self, layer):
        bounds = {}
        constricted = {}
        for i in range(81):
            if layer[i] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                bounds.setdefault(layer[i], []).append(f"S{i // 9 + 1}{i % 9+ 1}")
            elif layer[i] in "abcdefghijklmnopqrstuvwxyz":
                constricted.setdefault(layer[i], []).append(f"S{i // 9 + 1}{i % 9+ 1}")
        return bounds, constricted

    def random_rule(self):
        return list("A" + "a" * self.randint(1, 5) + "A")

    def to_html(self, layer):
        first = next((i for i in range(81) if layer[i] != "."), -1)
        if first < -1:
            return super().to_html()

        if self.is_horizontal(layer):
            return [f'<div class="constriction horizontal len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]

        else:
            return [f'<div class="constriction vertical len-{self.length(layer)}"></div>' if i == first else "" for i in range(81)]
