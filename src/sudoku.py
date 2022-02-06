"""
module responsible for acquiring layers
and solving the sudoku
"""
import re
import os
import random
import logging
import webbrowser
import subprocess
from z3 import Int, Solver, sat
from jinja2 import Environment, FileSystemLoader
from src.common.utils import clean
from src.common.connectives import and_clause
from src.rulesets.rulesets import RulesetManager


class Sudoku:

    def __init__(self, limboole, z3=False):
        self.logger = logging.getLogger("base.core")
        self.logger_indented = logging.getLogger("indented")

        self.RM = RulesetManager()
        self.rulesets = self.RM.get_rulesets()

        self.limboole = limboole

        self.z3 = z3
        self.init_layers()
        self.found_solutions = 0

    def init_layers(self):
        self.layers = {}
        self.add_layer("Basic Rules", "1-9 in every row, column, area")

    def add_layer(self, name, layer):
        self.layers.setdefault(name, [])
        self.layers[name].append(layer)

    def delete_layer(self, layer_string):
        name = layer_string.split(": ")[0].rstrip()
        layer = layer_string.split(": ")[1]

        self.layers[name].remove(layer)

    def get_available_layers(self):
        for key, value in self.rulesets.items():
            self.layers.setdefault(key, [])
            if value["max"] < 0 or len(self.layers[key]) < value["max"]:
                yield key

    def get_current_layers(self):
        for name, rules in self.layers.items():
            for rule in rules:
                yield f"{name.ljust(19)}: {rule}"

    def layer_from_cli(self):
        self.logger_indented.info(" ---------")

        layer = ""
        for i in range(9):
            layer += clean(input(f"                             {i + 1} |"), length=9)

        return layer

    def layer_from_string(self, layer):
        layer = clean(layer)
        return layer

    def layers_from_file(self, file):
        with open(file, "r") as f:
            raw = f.read()

        layers_raw = re.finditer(r"\[(?P<name>.*?)\](?P<layer>[^[]*)", raw, re.MULTILINE)
        for l_r in layers_raw:
            yield l_r.group("name"), clean(l_r.group("layer"))

    def write_to_file(self):
        file = ""
        while not file:
            file = input("    filename :: ")

        with open(file, "w") as f:
            for name, layers in self.layers.items():
                if name != "Basic Rules":
                    for layer in layers:
                        f.write(f"[{name}]\n")
                        f.writelines([" ".join(f"{layer[i:i + 9]}\n") for i in range(0, 81, 9)])
                        f.write("\n")

    def randomize_layers(self):
        for name, ruleset in self.rulesets.items():
            for layer in ruleset["instance"].random_layers():
                self.add_layer(name, layer)

    def generate_basic_sudoku(self, level=1):
        # Generate seed
        seed = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        random.shuffle(seed)
        seed = list(self.layer_from_string("".join(seed)))
        rnd = random.randint(0, 8) * 9
        seed[:] = seed[-rnd:] + seed[:-rnd]
        self.add_layer("Prefills", clean("".join(seed)))

        # get a solution from that seed
        solution = self.get_single_solution()

        # remove half of the hints until a unique solution is found
        uniquely_solvable = False
        while not uniquely_solvable:
            hints = "".join([k if random.randint(0, 1) == 0 else "." for k in solution])
            self.layers["Prefills"] = [hints]
            uniquely_solvable = self.get_solutions_info()["uniquely_solvable"]
        easy = hints

        medium = {}
        if level >= 2:
            uniquely_solvable = False
            while not uniquely_solvable:
                hints = "".join([k if random.randint(0, 5) > 1 else "." for k in easy])
                self.layers["Prefills"] = [hints]
                uniquely_solvable = self.get_solutions_info()["uniquely_solvable"]
            medium = {"hints_medium": hints}

        hard = {}
        if level >= 3:
            uniquely_solvable = False
            while not uniquely_solvable:
                hints = "".join([k if random.randint(0, 6) > 0 else "." for k in medium["hints_medium"]])
                self.layers["Prefills"] = [hints]
                uniquely_solvable = self.get_solutions_info()["uniquely_solvable"]
            hard = {"hints_hard": hints}

        return {
            "solution": solution,
            "hints_easy": easy
        } | medium | hard

    def get_single_solution(self):
        return "".join(list(self.find_solutions(max_new=1, blacklist_found=False))[0])

    def new_random_sudoku(self):
        # Step 1: generate a bunch of random rules, check that they are solvable
        self.randomize_layers()
        solutions = list(self.find_solutions(blacklist_found=False))

        while solutions == [0]:
            self.init_layers()
            self.randomize_layers()
            solutions = list(self.find_solutions(blacklist_found=False))

        # Step 2: use the first (probably non-unique) solution and add its entries in a random way until solution is unique
        # solution = solutions[0]

        # hint_order = [list(range(i, i+9)) for i in range(0, 81, 9)]

        # for i in hint_order:
        #    random.shuffle(i)
        # random.shuffle(hint_order)

        # hint_order = sum(hint_order, [])

        # hints = ["."] * 81
        # hint_count = 0

        # while len(solutions) != 1 and hint_count < 81:
        #    hints[hint_order[hint_count]] = solution[hint_order[hint_count]]
        #    self.layers["Prefills"] = ["".join(hints)]
        #    hint_count += 1
        #    solutions = list(self.find_solutions(blacklist_found=False))
        solution = "".join(solutions[0])
        self.generated_solution = solution

        uniquely_solvable = False
        while not uniquely_solvable:
            hints = "".join([k if random.randint(0, 3) == 0 else "." for k in solution])
            self.layers["Prefills"] = [hints]
            uniquely_solvable = self.get_solutions_info()["uniquely_solvable"]

    def solve(self):
        for solution in self.find_solutions():
            if solution == 0:
                if self.found_solutions == 0:
                    self.logger.error("Sudoku posseses no solution.")
                elif self.found_solutions == 1:
                    self.logger.info("Sudoku posseses exactly 1 solution.")
                else:
                    self.logger.info("All possible solutions found.")
            else:
                self.logger.info(f"New solution found! (Total: {self.found_solutions})")
                if self.layers["Prefills"] and len(self.layers["Prefills"]):
                    prefills = list(self.layers["Prefills"][0])
                else:
                    prefills = ["."] * 81
                self.prettify(solution, prefills)

    def get_solutions_info(self):
        solutions = list(self.find_solutions(max_new=2, blacklist_found=False))
        solvable = {}
        unique = {}
        if len(solutions) > 1:
            unique = {"uniquely_solvable": False}
        if solutions == [0]:
            solvable = {"solvable": False}
            solutions[0] = "unsolvable"
            unique = {"uniquely_solvable": False}
        return {
            "solvable": True,
            "uniquely_solvable": True,
            "solution": "".join(solutions[0])
        } | solvable | unique

    def find_solutions(self, blacklist_found=True, max_new=3):
        max_solutions = self.found_solutions + max_new
        satisfiable = True
        while self.found_solutions < max_solutions and satisfiable:
            formula = []
            for name, layers in self.layers.items():
                for layer in layers:
                    if self.z3:
                        f = self.rulesets[name]["instance"].to_smt(layer=layer)
                    else:
                        f = self.rulesets[name]["instance"].to_sat(layer=layer)
                    if f is not None:
                        formula.append(f)
            if self.z3:
                # formula = And(formula)

                s = Solver()
                s.add([item for sublist in formula for item in sublist])
                if s.check() == sat:
                    m = s.model()
                    solution = [str(m.evaluate(Int(f"S{i+1}{j+1}"))) for i in range(9) for j in range(9)]
                else:
                    satisfiable = False

            else:
                formula = and_clause(formula)

                with open("temp.txt", "w") as file:
                    file.write(formula)

                p = subprocess.Popen(f"{self.limboole} -s temp.txt", stdout=subprocess.PIPE, shell=True)
                (output, error) = p.communicate()
                p.wait()
                os.remove("temp.txt")

                if "UNSATISFIABLE formula" in str(output):
                    satisfiable = False

            if not satisfiable:
                if self.found_solutions == 0:
                    yield 0
            else:
                self.found_solutions += 1
                if not self.z3:
                    solution = self.extract_solution(str(output))
                self.add_layer("Blacklisted", "".join(solution))
                yield solution

        if not blacklist_found:
            self.layers["Blacklisted"] = []
            self.found_solutions = 0

    @staticmethod
    def extract_solution(output):
        solution = ["."] * 81

        matches = re.finditer(r"S(?P<i>\d)(?P<j>\d)(?P<k>\d) = 1", output, re.MULTILINE)
        for match in matches:
            i = int(match.group("i"))
            j = int(match.group("j"))
            k = match.group("k")
            solution[(j - 1) + (i - 1) * 9] = k

        return solution

    def prettify(self, solution, prefills):
        for i in range(81):
            if solution[i] != prefills[i]:
                solution[i] = "\033[92m" + solution[i] + "\033[0m"
        self.logger_indented.info("  ----- | ----- | -----")
        for i in range(9):
            line = solution[i*9:(i+1)*9]
            line.insert(3, " ")
            line.insert(7, " ")
            line = " ".join(line)
            self.logger_indented.info(f"| {line}")

            if i in [2, 5]:
                self.logger_indented.info("-")

    def force_rebuild(self):
        self.RM.force_rebuild()

    def get_rulesets(self):
        return self.rulesets

    def print_puzzle(self):
        fields = [""] * 81
        for name, layers in self.layers.items():
            if name not in ["Blacklisted", "Basic Rules"]:
                for layer in layers:
                    fields = [m+n for m, n in zip(fields, self.rulesets[name]["instance"].to_html(layer))]

        base = os.path.dirname(os.path.dirname(__file__))
        common = os.path.join(base, "src", "common")
        jinja = Environment(loader=FileSystemLoader(common))
        page_template = jinja.get_template("template.html")
        with open(os.path.join(base, "out.html"), "w") as file:
            file.write(page_template.render(fields=fields))

        webbrowser.open(f"file://{base}/out.html")
