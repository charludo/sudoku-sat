from fastapi import FastAPI
from pydantic import BaseModel
from typing import Set
from src.sudoku import Sudoku

app = FastAPI()


class Item(BaseModel):
    Prefills: str = "." * 81
    AreaSums: Set[str] = set()
    Constrictions: Set[str] = set()
    Counter: Set[str] = set()
    Evens: Set[str] = set()
    Odds: Set[str] = set()
    Thermometer: Set[str] = set()


@app.get("/check_if_solvable/{prefills}")
async def check_solvability(prefills: str):
    s = Sudoku()
    s.add_layer("Prefills", s.layer_from_string(prefills))
    return s.get_solutions_info()["solvable"]


@app.get("/solve/{prefills}")
async def solve_basic_sudoku(prefills: str):
    s = Sudoku()
    s.add_layer("Prefills", s.layer_from_string(prefills))
    return s.get_solutions_info()


@app.post("/solve")
async def solve_complex_sudoku(item: Item):
    return item


@app.get("/generate/easy")
async def generate_easy_sudoku():
    s = Sudoku()
    return s.generate_basic_sudoku()


@app.get("/generate/medium")
async def generate_medium_sudoku():
    s = Sudoku()
    return s.generate_basic_sudoku(level=2)


@app.get("/generate/hard")
async def generate_hard_sudoku():
    s = Sudoku()
    return s.generate_basic_sudoku(level=3)


@app.get("/generate/complex")
async def generate_complex_sudoku():
    s = Sudoku()
    s.new_random_sudoku()
    item = s.layers
    del item["Basic Rules"]
    del item["Blacklisted"]
    return item
