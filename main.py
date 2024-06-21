from typing import Union

from fastapi import FastAPI, BackgroundTasks

import elo_analysis
import generate_arena_tabl
import run_script
import generator
import utils
import os
import json
import utils

app = FastAPI()




@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/compute_elo")
def compute_elo(background_tasks: BackgroundTasks):
    utils.download_new_file()
    background_tasks.add_task(generate_arena_tabl.generate_arena_leaderboard_json)
    return {"ok"}


@app.get("/api/v1/leaderboard")
def leaderboard():
    folder_path = "./tables/arena_table"
    abs_path = os.path.abspath(folder_path)
    max_date_file = utils.get_max_date_json_files(abs_path, "arena_table_")
    if max_date_file:
        full_path = os.path.join(abs_path, max_date_file)
    else:
        return
    content = utils.read_json_file(full_path)
    with open('1.txt', 'w') as f:
        f.write(content)
    print(f"Content of the latest file ({max_date_file}):")
    print(json.dumps(content, indent=4, ensure_ascii=False))
    return {"ok"}


@app.get("/api/v1/elo_results")
def return_results():
    return generator.return_full_category_table()
