from typing import Union

from fastapi import FastAPI, BackgroundTasks

import run_script

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/compute_elo")
def compute_elo(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_script.run_script())

    return {"ok"}


@app.get("/leaderboard")
def leaderboard():
    return {"ok"}
