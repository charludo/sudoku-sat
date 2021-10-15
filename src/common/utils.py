import re
from os.path import join, dirname

ruleset_dir = join(dirname(dirname(__file__)), "rulesets")
static_dir = join(ruleset_dir, "static")


def write_static(path, content):
    with open(join(static_dir, path), "w") as file:
        file.write(content)


def read_static(path):
    with open(join(static_dir, path), "r") as file:
        return file.read()


def clean(layer, length=81):
    layer = layer.replace("\n", "")
    layer = layer.replace(" ", "")
    layer = re.sub(r"[^a-zA-Z0-9]", ".", layer)
    layer = layer.ljust(length, ".")[:length]
    return layer
