from src.rulesets.rulesets import Ruleset
from src.common.connectives import and_clause, grouped


class Prefills(Ruleset):

    def generate(self, sudoku):
        return grouped(and_clause([f"S{i // 9 + 1}{i % 9+ 1}{sudoku[i]}" for i in range(81) if sudoku[i] in "123456789"]))

    def register(self):
        return "Prefills"
