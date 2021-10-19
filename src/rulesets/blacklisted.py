import re
from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, grouped


class Blacklisted(Ruleset):

    def register(self):
        return "Blacklisted", "Complete solution that is blacklisted in order to find a new one.", -1

    def generate(self, layer):
        if len(re.sub(r"[^1-9]", "", layer)) != 81:
            return None

        clauses = [f"S{i // 9 + 1}{i % 9+ 1}{layer[i]}" for i in range(81)]
        return "!" + grouped(and_clause(clauses))
