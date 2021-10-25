"""
discover & load all available rulesets.
distinguishes between static and dynamic
rulesets.
"""

import os
import sys
import logging
from inspect import isclass
from pkgutil import iter_modules
from importlib import import_module
from abc import ABC, abstractmethod
from src.common.utils import ruleset_dir


class Ruleset(ABC):
    """ base class for all rulesets """
    from random import randint, shuffle

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("base.rule")
        self.logger_indented = logging.getLogger("indented")

    @abstractmethod
    def register(self):
        return "Base", "Help Text", 1

    @abstractmethod
    def to_sat(self, layer, *args, **kwargs):
        return layer

    # @abstractmethod
    def to_smt(self, layer, *args, **kwargs):
        return None

    def random_rule(self):
        return None

    def rebuild(self):
        pass

    def random_layers(self, max=7):
        lines = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.shuffle(lines)
        for line in lines[0:self.randint(0, max)]:
            rule = self.random_rule()
            if not rule:
                continue

            before_pad = [0 for i in range(self.randint(0, 9 - len(rule)))]
            after_pad = [0 for i in range(9 - len(rule) - len(before_pad))]
            rule = before_pad + rule + after_pad

            if self.randint(0, 1) == 0:
                yield self.to_row(rule, line)
            else:
                yield self.to_col(rule, line)

    def to_row(self, rule, row):
        str_row = "".join([str(x) if x != 0 else "." for x in rule])
        return "........." * row + str_row + "........." * (8 - row)

    def to_col(self, rule, col):
        str_col = "".join([str(x) if x != 0 else "." for x in rule])
        return "".join(["." * col + str_col[i] + "." * (8 - col) for i in range(9)])

    def to_html(self, layer):
        return [""] * 81

    def is_horizontal(self, layer):
        if layer.replace(".", "") in layer:
            return True
        return False

    def length(self, layer):
        return len(layer.replace(".", ""))


class RulesetManager:
    """ discovers, registers and pipes in rulesets """
    logger = logging.getLogger("base.core")

    ruleset_count = 0

    def __init__(self):
        self.logger.info("registering rulesets...")
        self.rulesets = self.discover_rulesets(ruleset_dir)
        self.logger.info(f"{self.ruleset_count} rulesets registered.")

    def discover_rulesets(self, path):
        """ checks the path for ruleset files, then imports them """
        self.logger.debug(f"checking for rulesets in {path}")

        module_paths = [path]
        if os.path.exists(path):
            subdirs = (next(os.walk(path))[1])                                  # get all first level subdirs
            module_paths.extend([os.path.join(path, sub) for sub in subdirs])   # necessary, otherwise wrong relative paths
        sys.path.extend(module_paths)                                           # necessary for python to import from here

        registered = []    # used to ensure no duplicate rulesets will be registered

        found_rulesets = {}
        for (_, module_name, _) in iter_modules(module_paths):
            try:
                module = import_module(f"{module_name}")
            except Exception:
                continue

            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                # necessary to filter out the imported parent class
                if isclass(attribute) and issubclass(attribute, Ruleset) and not issubclass(Ruleset, attribute):
                    try:
                        ruleset_instance = attribute()
                        name, help_text, max_layers = ruleset_instance.register()
                        if name in registered:
                            continue
                        registered.append(name)
                        self.logger.info(f"including ruleset: {name.upper()}")
                        self.ruleset_count += 1
                        found_rulesets[name] = {
                                "max": max_layers,
                                "help": help_text,
                                "instance": ruleset_instance
                            }
                    except Exception:
                        pass

        sys.path = list(set(sys.path) - set(module_paths))                      # remove our added entries to path

        return found_rulesets

    def force_rebuild(self):
        for ruleset in self.rulesets:
            ruleset.rebuild()

    def get_rulesets(self):
        return self.rulesets
