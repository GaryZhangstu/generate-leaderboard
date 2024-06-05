import argparse
import ast
from datetime import datetime
import json
import os
import pickle
import pandas as pd
import numpy as np
import re

from elo_analysis import return_full_category_table


def model_hyperlink(model_name, link):
    return f'<a target="_blank" href="{link}" style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'


def load_leaderboard_table_csv(filename, add_hyperlink=False):
    lines = open(filename).readlines()
    heads = [v.strip() for v in lines[0].split(",")]
    rows = []
    for i in range(1, len(lines)):
        row = [v.strip() for v in lines[i].split(",")]
        for j in range(len(heads)):
            item = {}
            for h, v in zip(heads, row):
                if h == "Arena Elo rating":
                    if v != "-":
                        v = int(ast.literal_eval(v))
                    else:
                        v = np.nan
                elif h == "MMLU":
                    if v != "-":
                        v = round(ast.literal_eval(v) * 100, 1)
                    else:
                        v = np.nan
                elif h == "MT-bench (win rate %)":
                    if v != "-":
                        v = round(ast.literal_eval(v[:-1]), 1)
                    else:
                        v = np.nan
                elif h == "MT-bench (score)":
                    if v != "-":
                        v = round(ast.literal_eval(v), 2)
                    else:
                        v = np.nan
                item[h] = v
            if add_hyperlink:
                item["Model"] = model_hyperlink(item["Model"], item["Link"])
        rows.append(item)
    return rows


def recompute_final_ranking(arena_df):
    ranking = {}
    for i, model_a in enumerate(arena_df.index):
        ranking[model_a] = 1
        for j, model_b in enumerate(arena_df.index):
            if i == j:
                continue
            if (
                    arena_df.loc[model_b]["rating_q025"]
                    > arena_df.loc[model_a]["rating_q975"]
            ):
                ranking[model_a] += 1
    return list(ranking.values())


def create_ranking_str(ranking, ranking_difference):
    if ranking_difference > 0:
        return f"{int(ranking)} \u2191"
    elif ranking_difference < 0:
        return f"{int(ranking)} \u2193"
    else:
        return f"{int(ranking)}"


def get_arena_table(arena_df, model_table_df, arena_subset_df=None):
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
            model_name = model_table_df[model_table_df["key"] == model_key][
                "Model"
            ].values[0]
            # rank
            ranking = arena_df.iloc[i].get("final_ranking") or i + 1
            row.append(ranking)
            if arena_subset_df is not None:
                row.append(arena_df.iloc[i].get("ranking_difference") or 0)
            # model display name
            row.append(model_name)
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
            # Organization
            row.append(
                model_table_df[model_table_df["key"] == model_key][
                    "Organization"
                ].values[0]
            )
            # license
            row.append(
                model_table_df[model_table_df["key"] == model_key]["License"].values[0]
            )
            cutoff_date = model_table_df[model_table_df["key"] == model_key][
                "Knowledge cutoff date"
            ].values[0]
            if cutoff_date == "-":
                row.append("Unknown")
            else:
                row.append(cutoff_date)
            values.append(row)
        except Exception as e:
            print(f"{model_key} - {e}")
    return values


def find_max_numbered_file(prefix, directory):
    """
    查找以特定前缀开头，并且后面跟着的最大数字的文件名。

    :param prefix: 文件名前缀，如 'model_table_'
    :param directory: 要搜索的目录路径
    :return: 最大数字对应的完整文件名，如果没有找到则返回None
    """
    # 正则表达式，匹配前缀后的数字
    pattern = re.compile(re.escape(prefix) + "\\d+")



    max_number = -1
    max_filename = None

    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
                max_filename = filename

    return max_filename


def generate_arena_leaderboard_json(leaderboard_table_file=None, elo_results_file=None, ):
    if elo_results_file:
        with open(elo_results_file, "rb") as fin:
            elo_results = pickle.load(fin)
    else:
        elo_results = return_full_category_table()

    if leaderboard_table_file is None:
        leaderboard_table_file = find_max_numbered_file('model_table_', './tables/model_table')

    data = load_leaderboard_table_csv(leaderboard_table_file)
    model_table_df = pd.DataFrame(data)

    all_data = []

    for i in ["full", "chinese", "english"]:
        if elo_results[i]:
            arena_df = elo_results[i]["leaderboard_table_df"]

            arena_values = get_arena_table(arena_df, model_table_df)

            column_names = [
                "Rank* (UB)",
                "Model",
                "Elo",
                "95% CI",
                "Votes",
                "Organization",
                "License",
                "Knowledge Cutoff Date"
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

    print(f"Arena leaderboard JSON saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--elo-results-file", type=str, required=True)
    parser.add_argument("--leaderboard-table-file", type=str, required=True)
    parser.add_argument("--output-file", type=str, required=True)
    args = parser.parse_args()

    generate_arena_leaderboard_json(args.elo_results_file, args.leaderboard_table_file, args.output_file)
