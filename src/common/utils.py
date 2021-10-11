from os.path import join, dirname

ruleset_dir = join(dirname(dirname(__file__)), "rulesets")
static_dir = join(ruleset_dir, "static")


def write_static(path, content):
    with open(join(static_dir, path), "w") as file:
        file.write(content)


def read_static(path):
    with open(join(static_dir, path), "r") as file:
        return file.read()
