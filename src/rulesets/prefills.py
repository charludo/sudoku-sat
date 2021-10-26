from z3 import Int
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, grouped


class Prefills(Ruleset):

    def to_sat(self, layer):
        clauses = [f"S{i // 9 + 1}{i % 9+ 1}{layer[i]}" for i in range(81) if layer[i] in "123456789"]
        return grouped(and_clause(clauses)) if len(clauses) else None

    def to_smt(self, layer):
        return [Int(f"S{i // 9 + 1}{i % 9+ 1}") == int(layer[i]) for i in range(81) if layer[i] in "123456789"]

    def register(self):
        return "Prefills", "Allowed Characters: 123456789 and .", 1

    def to_html(self, layer):
        return [layer[i] if layer[i] != "." else "" for i in range(81)]
