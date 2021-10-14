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

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("base.rule")
        self.logger_indented = logging.getLogger("indented")

    @abstractmethod
    def register(self):
        return "Base"

    @abstractmethod
    def generate(self, sudoku, *args, **kwargs):
        return sudoku

    def rebuild(self):
        pass


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

        found_rulesets = []
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
                        name = ruleset_instance.register()
                        if name in registered:
                            continue
                        registered.append(name)
                        self.logger.info(f"including ruleset: {name.upper()}")
                        self.ruleset_count += 1
                        found_rulesets.append(ruleset_instance)
                    except Exception:
                        pass

        sys.path = list(set(sys.path) - set(module_paths))                      # remove our added entries to path

        return found_rulesets

    def force_rebuild(self):
        for ruleset in self.rulesets:
            ruleset.rebuild()

    def hook_rules(self, sudoku):
        for ruleset in self.rulesets:
            formula = ruleset.generate(sudoku=sudoku)
            if formula:
                yield formula.rstrip()
