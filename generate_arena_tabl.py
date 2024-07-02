import json
import os
import pickle
from datetime import datetime
import config.oss_config as oss
import requests

import pandas as pd

from elo_analysis import return_full_category_table
from generator import recompute_final_ranking, create_ranking_str


def get_arena_table(arena_df, arena_subset_df=None):
    arena_df = arena_df.sort_values(
        by=["final_ranking", "rating"], ascending=[True, False]
    )
    arena_df["final_ranking"] = recompute_final_ranking(arena_df)
    arena_df = arena_df.sort_values(by=["final_ranking"], ascending=True)

    # sort by rating
    if arena_subset_df is not None:
        # filter out models not in the arena_df
        arena_subset_df = arena_subset_df[arena_subset_df.index.isin(arena_df.index)]
        arena_subset_df = arena_subset_df.sort_values(by=["rating"], ascending=False)
        arena_subset_df["final_ranking"] = recompute_final_ranking(arena_subset_df)
        # keep only the models in the subset in arena_df and recompute final_ranking
        arena_df = arena_df[arena_df.index.isin(arena_subset_df.index)]
        # recompute final ranking
        arena_df["final_ranking"] = recompute_final_ranking(arena_df)

        # assign ranking by the order
        arena_subset_df["final_ranking_no_tie"] = range(1, len(arena_subset_df) + 1)
        arena_df["final_ranking_no_tie"] = range(1, len(arena_df) + 1)
        # join arena_df and arena_subset_df on index
        arena_df = arena_subset_df.join(
            arena_df["final_ranking"], rsuffix="_global", how="inner"
        )
        arena_df["ranking_difference"] = (
                arena_df["final_ranking_global"] - arena_df["final_ranking"]
        )

        arena_df = arena_df.sort_values(
            by=["final_ranking", "rating"], ascending=[True, False]
        )
        arena_df["final_ranking"] = arena_df.apply(
            lambda x: create_ranking_str(x["final_ranking"], x["ranking_difference"]),
            axis=1,
        )

    arena_df["final_ranking"] = arena_df["final_ranking"].astype(str)

    values = []
    for i in range(len(arena_df)):
        row = []
        model_key = arena_df.index[i]
        try:  # this is a janky fix for where the model key is not in the model table (model table and arena table dont contain all the same models)
            model_key = model_key
            # rank
            ranking = arena_df.iloc[i].get("final_ranking") or i + 1
            row.append(ranking)
            if arena_subset_df is not None:
                row.append(arena_df.iloc[i].get("ranking_difference") or 0)
            # model display name
            row.append(model_key)
            # elo rating
            row.append(round(arena_df.iloc[i]["rating"]))
            upper_diff = round(
                arena_df.iloc[i]["rating_q975"] - arena_df.iloc[i]["rating"]
            )
            lower_diff = round(
                arena_df.iloc[i]["rating"] - arena_df.iloc[i]["rating_q025"]
            )
            row.append(f"+{upper_diff}/-{lower_diff}")
            # num battles
            row.append(round(arena_df.iloc[i]["num_battles"]))

            # license

            values.append(row)
        except Exception as e:
            print(f"{model_key} - {e}")
    return values


def generate_arena_leaderboard_json(leaderboard_table_file=None, elo_results_file=None, ):
    if elo_results_file:
        with open(elo_results_file, "rb") as fin:
            elo_results = pickle.load(fin)
    else:

        elo_results = return_full_category_table()

    all_data = []

    for i in ["full"]:
        if elo_results[i]:
            arena_df = elo_results[i]["leaderboard_table_df"]

            arena_values = get_arena_table(arena_df)

            column_names = [
                "rank",
                "model",
                "elo",
                "ci",
                "votes"
            ]
            arena_table = pd.DataFrame(arena_values, columns=column_names)
            result_dict = arena_table.to_dict(orient='records')
            return_data = {
                "dataSource": elo_results[i]["rating_system"],
                "category": i,
                "lastUpdated": elo_results[i]['last_updated_datetime'],
                "arena_table": result_dict,

            }
            all_data.append(return_data)

    folder_path = "./tables/arena_table"
    abs_path = os.path.abspath(folder_path)

    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = os.path.join(abs_path, f"arena_table_{current_datetime}.json")

    with open(output_file, "w") as fout:
        json.dump(all_data, fout)


def generate_arena_leaderboard_json_with_retry():

    url = "http://120.0.0.1:8085/is_success/"
    compute_state = "true"
    try:
        generate_arena_leaderboard_json()
    except:
        compute_state = "false"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(
        url+compute_state,
        headers=headers,
    )



if __name__ == "__main__":
    generate_arena_leaderboard_json()
