from z3 import Int, Or, And
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped


class Odds(Ruleset):

    def register(self):
        return "Odds", "Mark fields which must contain odd numbers.", 1

    def to_sat(self, layer):
        fields = [f"S{i // 9 + 1}{i % 9+ 1}" for i in range(81) if layer[i] != "."]

        return grouped(and_clause([grouped(or_clause([field + str(i) for i in "13579"])) for field in fields])) if len(fields) else None

    def to_smt(self, layer):
        fields = [f"S{i // 9 + 1}{i % 9+ 1}" for i in range(81) if layer[i] != "."]

        return [And(*[Or(*[Int(f) == o for o in [1, 3, 5, 7, 9]]) for f in fields])]

    def random_rule(self):
        return ["O"]

    def to_html(self, layer):
        return ['<div class="odd"></div>' if layer[i] != "." else "" for i in range(81)]
