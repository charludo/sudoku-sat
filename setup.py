import setuptools

setuptools.setup(name='sudoku-sat',
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 entry_points={"console_scripts": ["sudoku-sat = src.cli:run"]},
                 install_requires=[
                    "click>=8.0.0",
                    "coloredlogs>=15.0.0"
                 ]
                 )
