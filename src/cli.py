import re
import os
import click
import logging
import subprocess
import coloredlogs
from src.rulesets.rulesets import RulesetManager
from src.common.connectives import and_clause


def setup_loggers(level):
    # filter to only show last part of logger name
    class ShortNameFilter(logging.Filter):
        def filter(self, record):
            record.name = record.name.rsplit('.', 1)[-1]
            return True

    base = logging.getLogger("base")
    format = "[sudoku-sat][%(name)6s][%(levelname)5s] :: %(message)s"
    style = coloredlogs.DEFAULT_FIELD_STYLES | {"levelname": {"bold": False, "color": 244}}
    coloredlogs.install(level=level, logger=base, fmt=format, field_styles=style)

    for handler in base.handlers:
        handler.addFilter(ShortNameFilter())

    global logger
    logger = logging.getLogger("base.core")

    global logger_indented
    logger_indented = logging.getLogger("indented")
    format_indented = "                            -> %(message)s"
    coloredlogs.install(level=level, logger=logger_indented, fmt=format_indented)

    logger.debug("Logging setup complete")


@click.command()
@click.option("--force-rebuild", "-r", help="force a rebuild of static rulesets", is_flag=True)
@click.option("--from-file", "-f", help="read sudoku from a file")
@click.option("--from-string", "-s", help="pass an 81-char sudoku string")
@click.option("--debug", "-d", help="set logging level to debug", is_flag=True)
def run(debug, from_string, from_file, force_rebuild):
    """
    sudoku-sat generates SAT formulas for sudokus with optional additional rulesets
    """
    setup_loggers("DEBUG" if debug else "INFO")

    global RM
    RM = RulesetManager()

    if force_rebuild:
        logger.info("rebuilding all static rulesets...")
        RM.force_rebuild()
        logger.info("done rebuilding static rulesets.")

    if from_string:
        layer_from_string(from_string)
    elif from_file:
        layer_from_file(from_file)
    else:
        logger.info("Enter a new sudoku.")
        logger.info("Allowed Characters: 123456789 and .")
        layer_from_cli()


def layer_from_cli():
    logger_indented.info(" ---------")

    sudoku = ""
    for i in range(9):
        sudoku += clean(input(f"                             {i + 1} |"), length=9)

    solve(sudoku)


def layer_from_string(sudoku):
    sudoku = clean(sudoku)
    solve(sudoku)


def layer_from_file(file):
    with open(file, "r") as f:
        sudoku = clean(f.read())

    solve(sudoku)


def clean(layer, length=81):
    layer = layer.replace("\n", "")
    layer = re.sub(r"[^a-zA-Z0-9]", ".", layer)
    layer = layer.ljust(length, ".")[:length]
    return layer


def solve(sudoku):
    formula = and_clause(RM.hook_rules(sudoku))

    with open("temp.txt", "w") as file:
        file.write(formula)

    p = subprocess.Popen("../limboole1.2/limboole -s temp.txt", stdout=subprocess.PIPE, shell=True)
    (output, error) = p.communicate()
    p.wait()
    os.remove("temp.txt")

    if "UNSATISFIABLE formula" in str(output):
        logger.error("Sudoku posseses no solution.")
    else:
        logger.info("Solution found!")
        logger_indented.info("  ----- | ----- | -----")
        solution = extract_solution(str(output))

        prettify(solution)


def extract_solution(output):
    solution = ["."] * 81

    matches = re.finditer(r"S(?P<i>\d)(?P<j>\d)(?P<k>\d) = 1", output, re.MULTILINE)
    for match in matches:
        i = int(match.group("i"))
        j = int(match.group("j"))
        k = match.group("k")
        solution[(j - 1) + (i - 1) * 9] = k

    return solution


def prettify(solution):
    for i in range(9):
        line = solution[i*9:(i+1)*9]
        line.insert(3, " ")
        line.insert(7, " ")
        line = " ".join(line)
        logger_indented.info(f"| {line}")

        if i in [2, 5]:
            logger_indented.info("-")
