from typing import Union

from fastapi import FastAPI, BackgroundTasks

import run_script
import generator
import utils
import os
import json

app = FastAPI()

leaderboard_file = 'example.csv'


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/v1/compute_elo")
def compute_elo(background_tasks: BackgroundTasks):
    background_tasks.add_task(generator.generate_arena_leaderboard_json())

    return {"ok"}


@app.get("/api/v1/leaderboard")
def leaderboard():

    folder_path = "./tables/arena_table"
    abs_path = os.path.abspath(folder_path)
    max_date_file = utils.get_max_date_json_files(abs_path,"arena_table_")
    if max_date_file:
        full_path = os.path.join(abs_path, max_date_file)
    else:
        return
    content = utils.read_json_file(full_path)
    print(f"Content of the latest file ({max_date_file}):")

    return json.dumps(content)
