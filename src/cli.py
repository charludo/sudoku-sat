import re
import click
import logging
import coloredlogs


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
@click.option("--from-file", "-f", help="read sudoku from a file")
@click.option("--from-string", "-s", help="pass an 81-char sudoku string")
@click.option("--debug", "-d", help="set logging level to debug", is_flag=True)
def run(debug, from_string, from_file):
    """
    sudoku-sat generates SAT formulas for sudokus with optional additional rulesets
    """
    setup_loggers("DEBUG" if debug else "INFO")

    if from_string:
        new_from_string(from_string)
    elif from_file:
        new_from_file(from_file)
    else:
        new_from_cli()


def new_from_cli():
    logger.info("Enter a new sudoku.")
    logger.info("Allowed Characters: 123456789 and .")
    logger_indented.info(" ---------")

    sudoku = ""
    for i in range(9):
        sudoku += input(f"                             {i} |").ljust(9, ".")[:9].replace(" ", ".")

    print(len(sudoku))


def new_from_string(sudoku):
    sudoku = sudoku.ljust(81, ".")[:81].replace(" ", ".")
    print(sudoku)


def new_from_file(file):
    with open(file, "r") as f:
        sudoku = f.read()

    sudoku = sudoku.replace("\n", "")
    sudoku = re.sub(r"[^1-9]", ".", sudoku)
    sudoku = sudoku.ljust(81, ".")[:81]

    print(sudoku)
