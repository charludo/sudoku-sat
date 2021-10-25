from z3 import And, Int, Distinct
from src.rulesets.rulesets import Ruleset
from src.common.utils import write_static, read_static
from src.common.connectives import and_clause, or_clause, grouped, ks


class BasicRules(Ruleset):

    def register(self):
        return "Basic Rules", " ", 1

    def to_sat(self, **kwargs):
        try:
            return read_static("basic_rules.txt")
        except FileNotFoundError:
            self.rebuild()
            self.generate()
            return read_static("basic_rules.txt")

    def rebuild(self):
        rows = and_clause([self.row(i) for i in ks])
        columns = and_clause([self.column(j) for j in ks])
        areas = and_clause([self.area(a) for a in ks])
        basic_rules = and_clause([self.number_everywhere(), self.no_double_entries(), rows, columns, areas])

        write_static("basic_rules.txt", basic_rules)

        write_static("basic_rules_smt.txt", self.z3_rules())

    @staticmethod
    def number_everywhere():
        return and_clause([grouped(or_clause([f"S{i}{j}{k}" for k in ks])) for i in ks for j in ks])

    @staticmethod
    def no_double_entries():
        return and_clause([grouped(and_clause([f"(!S{i}{j}{k1} | !S{i}{j}{k2})" for k1 in ks for k2 in ks if k1 < k2])) for i in ks for j in ks])

    @staticmethod
    def row(i):
        return and_clause([grouped(and_clause([f"(!S{i}{j1}{k} | !S{i}{j2}{k})" for k in ks])) for j1 in ks for j2 in ks if j1 < j2])

    @staticmethod
    def column(j):
        return and_clause([grouped(and_clause([f"(!S{i1}{j}{k} | !S{i2}{j}{k})" for k in ks])) for i1 in ks for i2 in ks if i1 < i2])

    @staticmethod
    def area(a):
        """
        area numbering scheme:
            1   2   3
            4   5   6
            7   8   9
        1 -> i=1, j=1
        2 -> i=1, j=4
        3 -> i=1, j=7

        4 -> i=4, j=1
        5 -> i=4, j=4
        6 -> i=4, j=7

        7 -> i=7, j=1
        8 -> i=7, j=4
        9 -> i=7, j=7
        """
        i_start = ((a - 1) // 3) * 3 + 1
        j_start = ((a - 1) % 3) * 3 + 1
        iv = range(i_start, i_start + 3)
        jv = range(j_start, j_start + 3)

        positions = [f"{i}{j}" for i in iv for j in jv]

        return and_clause([grouped(and_clause([f"(!S{p1}{k} | !S{p2}{k})" for k in ks])) for p1 in positions for p2 in positions if p1 != p2])

    def to_smt(self, **kwargs):
        """ smt logic roughly follows this guide: https://ericpony.github.io/z3py-tutorial/guide-examples.htm """
        x = [[Int(f"S{i}{j}") for j in ks] for i in ks]

        constrained_cells = [And(1 <= x[i][j], x[i][j] <= 9) for i in range(9) for j in range(9)]
        constrained_rows = [Distinct(x[i]) for i in range(9)]
        constrained_cols = [Distinct([x[i][j] for i in range(9)]) for j in range(9)]

        constrained_area = [Distinct([x[3*i0 + i][3*j0 + j] for i in range(3) for j in range(3)]) for i0 in range(3) for j0 in range(3)]

        return constrained_cells + constrained_rows + constrained_cols + constrained_area
