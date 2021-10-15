import click
import logging
import coloredlogs
from simple_term_menu import TerminalMenu as TM
from src.sudoku import Sudoku


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

    s = Sudoku()

    rulesets = s.get_rulesets()

    if force_rebuild:
        logger.info("rebuilding all static rulesets...")
        s.force_rebuild()
        logger.info("done rebuilding static rulesets.")

    choices = [*s.get_available_layers(), "[d] delete layer", "[s] solve sudoku", "[e] exit"]
    action = choices.index("Prefills")

    if from_string:
        layer = s.layer_from_string(from_string)
        s.add_layer("Prefills", layer)
        action = -1
    elif from_file:
        layers = s.layers_from_file(from_file)
        for name, layer in layers:
            s.add_layer(name, layer)
        action = -1

    while action != len(choices) - 1:
        # do nothing
        if action == -1:
            pass

        # solve!
        elif action == len(choices) - 2:
            s.solve()

        # delete layer
        elif action == len(choices) - 3:
            layers = [*s.get_current_layers(), "[a] abort"]
            tm = TM(layers)
            action = tm.show()

            if action != len(layers) - 1:
                s.delete_layer(layers[action])

        # add layer
        else:
            name = choices[action]
            help = rulesets[name]["help"]

            logger.info(f"Ruleset Layer: {name}")
            logger.info(help)

            layer = s.layer_from_cli()
            s.add_layer(name, layer)

            logger.debug(f"Added new layer of type {name}:")
            logger.debug(layer)

        # next selection
        logger.info("Add layer / delete layer / solve / exit:")
        choices = [*s.get_available_layers(), "[d] delete layer", "[s] solve sudoku", "[e] exit"]
        tm = TM(choices)
        action = tm.show()
