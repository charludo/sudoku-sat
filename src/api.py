from fastapi import FastAPI
from pydantic import BaseModel
from typing import Set
from src.sudoku import Sudoku

app = FastAPI()


class Item(BaseModel):
    prefills: str = "." * 81
    areasums: Set[str] = set()
    constrictions: Set[str] = set()
    counter: Set[str] = set()
    evens: Set[str] = set()
    odds: Set[str] = set()
    thermometer: Set[str] = set()


@app.get("/check_if_solvable/{prefills}")
async def check_solvability(prefills: str):
    s = Sudoku()
    s.add_layer("Prefills", s.layer_from_string(prefills))
    return s.get_solutions_info()["solvable"]


@app.get("/solve_basic/{prefills}")
async def solve_basic_sudoku(prefills: str):
    s = Sudoku()
    s.add_layer("Prefills", s.layer_from_string(prefills))
    return s.get_solutions_info()


@app.post("/solve_complex")
async def solve_complex_sudoku(item: Item):
    return item.evens


@app.get("/generate_basic")
async def generatew_basic_sudoku():
    s = Sudoku()
    s.new_random_sudoku(complex=False)
    return s.layers["Prefills"][0]
