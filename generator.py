import argparse
import ast
import json
import pickle
import pandas as pd
import numpy as np


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

def get_arena_table1(arena_df, model_table_df, arena_subset_df=None):
    arena_df = arena_df.sort_values(by=["final_ranking", "rating"], ascending=[True, False])
    arena_df["final_ranking"] = recompute_final_ranking(arena_df)
    arena_df = arena_df.sort_values(by=["final_ranking"], ascending=True)

    if arena_subset_df is not None:
        arena_subset_df = arena_subset_df[arena_subset_df.index.isin(arena_df.index)]
        arena_subset_df = arena_subset_df.sort_values(by=["rating"], ascending=False)
        arena_subset_df["final_ranking"] = recompute_final_ranking(arena_subset_df)
        arena_df = arena_df[arena_df.index.isin(arena_subset_df.index)]
        arena_df["final_ranking"] = recompute_final_ranking(arena_df)
        arena_subset_df["final_ranking_no_tie"] = range(1, len(arena_subset_df) + 1)
        arena_df["final_ranking_no_tie"] = range(1, len(arena_df) + 1)
        arena_df = arena_subset_df.join(arena_df["final_ranking"], rsuffix="_global", how="inner")
        arena_df["ranking_difference"] = arena_df["final_ranking_global"] - arena_df["final_ranking"]
        arena_df = arena_df.sort_values(by=["final_ranking", "rating"], ascending=[True, False])
        arena_df["final_ranking"] = arena_df.apply(lambda x: create_ranking_str(x["final_ranking"], x["ranking_difference"]), axis=1)

    arena_df["final_ranking"] = arena_df["final_ranking"].astype(str)
    values = []
    for i in range(len(arena_df)):
        model_key = arena_df.index[i]
        if model_key in model_table_df.index:
            try:
                model_name = model_table_df.loc[model_key, "Model"]
                ranking = arena_df.iloc[i].get("final_ranking") or i + 1
                row = [ranking]
                if arena_subset_df is not None:
                    row.append(arena_df.iloc[i].get("ranking_difference") or 0)
                row.append(model_name)
                row.append(round(arena_df.iloc[i]["rating"]))
                upper_diff = round(arena_df.iloc[i]["rating_q975"] - arena_df.iloc[i]["rating"])
                lower_diff = round(arena_df.iloc[i]["rating"] - arena_df.iloc[i]["rating_q025"])
                row.append(f"+{upper_diff}/-{lower_diff}")
                row.append(round(arena_df.iloc[i]["num_battles"]))
                row.append(model_table_df.loc[model_key, "Organization"])
                row.append(model_table_df.loc[model_key, "License"])
                cutoff_date = model_table_df.loc[model_key, "Knowledge cutoff date"]
                row.append("Unknown" if cutoff_date == "-" else cutoff_date)
                values.append(row)
            except Exception as e:
                print(f"{model_key} - {e}")
        else:
            print(f"Model key {model_key} not found in model_table_df")
    return values

def get_arena_table(arena_df, model_table_df, arena_subset_df=None):
    print(arena_df.index)
    print(model_table_df.index)
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
def get_arena_table2(arena_df, model_table_df, arena_subset_df=None):
    arena_df = arena_df.sort_values(by=["final_ranking", "rating"], ascending=[True, False])
    arena_df["final_ranking"] = recompute_final_ranking(arena_df)
    arena_df = arena_df.sort_values(by=["final_ranking"], ascending=True)

    if arena_subset_df is not None:
        arena_subset_df = arena_subset_df[arena_subset_df.index.isin(arena_df.index)]
        arena_subset_df = arena_subset_df.sort_values(by=["rating"], ascending=False)
        arena_subset_df["final_ranking"] = recompute_final_ranking(arena_subset_df)
        arena_df = arena_df[arena_df.index.isin(arena_subset_df.index)]
        arena_df["final_ranking"] = recompute_final_ranking(arena_df)
        arena_subset_df["final_ranking_no_tie"] = range(1, len(arena_subset_df) + 1)
        arena_df["final_ranking_no_tie"] = range(1, len(arena_df) + 1)
        arena_df = arena_subset_df.join(arena_df["final_ranking"], rsuffix="_global", how="inner")
        arena_df["ranking_difference"] = arena_df["final_ranking_global"] - arena_df["final_ranking"]
        arena_df = arena_df.sort_values(by=["final_ranking", "rating"], ascending=[True, False])
        arena_df["final_ranking"] = arena_df.apply(lambda x: create_ranking_str(x["final_ranking"], x["ranking_difference"]), axis=1)

    arena_df["final_ranking"] = arena_df["final_ranking"].astype(str)

    values = []
    print(model_table_df)

    for i in range(len(arena_df)):

        model_key = arena_df.index[i]
        print(model_key,11111111111,model_table_df.index)
        print(model_table_df["Model"])
        model_table_df.reset_index('Model')
        if model_key in model_table_df.index:
            try:
                model_name = model_table_df.loc[model_key, "Model"]
                ranking = arena_df.iloc[i].get("final_ranking") or i + 1
                row = [ranking]
                if arena_subset_df is not None:
                    row.append(arena_df.iloc[i].get("ranking_difference") or 0)
                row.append(model_name)
                row.append(round(arena_df.iloc[i]["rating"]))
                upper_diff = round(arena_df.iloc[i]["rating_q975"] - arena_df.iloc[i]["rating"])
                lower_diff = round(arena_df.iloc[i]["rating"] - arena_df.iloc[i]["rating_q025"])
                row.append(f"+{upper_diff}/-{lower_diff}")
                row.append(round(arena_df.iloc[i]["num_battles"]))
                row.append(model_table_df.loc[model_key, "Organization"])
                row.append(model_table_df.loc[model_key, "License"])
                cutoff_date = model_table_df.loc[model_key, "Knowledge cutoff date"]
                row.append("Unknown" if cutoff_date == "-" else cutoff_date)
                values.append(row)
            except Exception as e:
                print(f"{model_key} - {e}")
        else:
            print(f"Model key {model_key} not found in model_table_df")
    return values

def generate_arena_leaderboard_json(elo_results_file, leaderboard_table_file, output_file):
    with open(elo_results_file, "rb") as fin:
        elo_results = pickle.load(fin)

    data = load_leaderboard_table_csv(leaderboard_table_file)
    model_table_df = pd.DataFrame(data)
    print(model_table_df)
    all_data = []

    for i in ["full", "chinese", "english"]:
        if elo_results[i]:
            arena_df = elo_results[i]["leaderboard_table_df"]
            arena_df = pd.DataFrame(arena_df)
            arena_table = get_arena_table2(arena_df, model_table_df)

            return_data = {
                "dataSource": elo_results[i]["rating_system"],
                "category": i,
                "lastUpdated": elo_results[i]['last_updated_datetime'],
                "arena_table": arena_table,

            }
            all_data.append(return_data)
    with open(output_file, "w") as fout:
        json.dump(all_data, fout, indent=4)

    print(f"Arena leaderboard JSON saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--elo-results-file", type=str, required=True)
    parser.add_argument("--leaderboard-table-file", type=str, required=True)
    parser.add_argument("--output-file", type=str, required=True)
    args = parser.parse_args()

    generate_arena_leaderboard_json(args.elo_results_file, args.leaderboard_table_file, args.output_file)
