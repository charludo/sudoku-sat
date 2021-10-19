from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, grouped


class Prefills(Ruleset):

    def to_sat(self, layer):
        clauses = [f"S{i // 9 + 1}{i % 9+ 1}{layer[i]}" for i in range(81) if layer[i] in "123456789"]
        return grouped(and_clause(clauses)) if len(clauses) else None

    def register(self):
        return "Prefills", "Allowed Characters: 123456789 and .", 1
