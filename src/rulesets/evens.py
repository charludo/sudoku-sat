from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, or_clause, grouped


class Evens(Ruleset):

    def register(self):
        return "Evens", "Mark fields which must contain even numbers.", 1

    def generate(self, layer):
        fields = [f"S{i // 9 + 1}{i % 9+ 1}" for i in range(81) if layer[i] != "."]

        return grouped(and_clause([grouped(or_clause([field + str(i) for i in "2468"])) for field in fields])) if len(fields) else None