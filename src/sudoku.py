"""
module responsible for acquiring layers
and solving the sudoku
"""
import re
import os
import logging
import subprocess
from src.common.utils import clean
from src.common.connectives import and_clause
from src.rulesets.rulesets import RulesetManager


class Sudoku:

    def __init__(self):
        self.logger = logging.getLogger("base.core")
        self.logger_indented = logging.getLogger("indented")
        self.RM = RulesetManager()
        self.rulesets = self.RM.get_rulesets()
        self.layers = {}
        self.add_layer("Basic Rules", "1-9 in every row, column, area")
        self.found_solutions = 0

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

    def solve(self):
        max_solutions = self.found_solutions + 3
        satisfiable = True
        while self.found_solutions < max_solutions and satisfiable:
            formula = []
            for name, layers in self.layers.items():
                for layer in layers:
                    f = self.rulesets[name]["instance"].to_sat(layer=layer)
                    if f:
                        formula.append(f)
            formula = and_clause(formula)

            with open("temp.txt", "w") as file:
                file.write(formula)

            p = subprocess.Popen("../limboole1.2/limboole -s temp.txt", stdout=subprocess.PIPE, shell=True)
            (output, error) = p.communicate()
            p.wait()
            os.remove("temp.txt")

            if "UNSATISFIABLE formula" in str(output):
                if self.found_solutions == 0:
                    self.logger.error("Sudoku posseses no solution.")
                elif self.found_solutions == 1:
                    self.logger.info("Sudoku posseses exactly 1 solution.")
                else:
                    self.logger.info("All possible solutions found.")
                satisfiable = False
            else:
                self.found_solutions += 1
                self.logger.info(f"New solution found! (Total: {self.found_solutions})")
                self.logger_indented.info("  ----- | ----- | -----")
                solution = self.extract_solution(str(output))
                self.prettify(solution)

                self.add_layer("Blacklisted", "".join(solution))

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

    def prettify(self, solution):
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
