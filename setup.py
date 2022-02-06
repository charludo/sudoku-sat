import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(name='sudoku-sat',
                 version="1.0.0",

                 description='Solve and generate basic Sudokus and Sudokus with an extended set of rules.',
                 long_description=README,
                 long_description_content_type="text/markdown",
                 keywords=['sudoku', 'sat'],
                 url='https://github.com/charludo/sudoku-sat',
                 author='Charlotte Hartmann Paludo',
                 author_email='charlotte.hartmann-paludo@stud.uni-due.de',
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 zip_safe=False,

                 entry_points={"console_scripts": ["sudoku-sat = src.cli:run"]},
                 install_requires=[
                    "click>=8.0.0",
                    "coloredlogs>=15.0.0",
                    "simple-term-menu>=1.4.1",
                    "Jinja2>=3.0.2",
                    "z3-solver>=4.8.12.0"
                 ]
                 )
