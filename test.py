import json
import os
import utils
from config.oss_config import upload_file
from elo_analysis import return_full_category_table

# folder_path = "./tables/arena_table"
# abs_path = os.path.abspath(folder_path)
# max_date_file = utils.get_max_date_json_files(abs_path,"arena_table_")
# if max_date_file:
#     full_path = os.path.join(abs_path, max_date_file)
# else:
#     print('111')
# content = utils.read_json_file(full_path)
# print(f"Content of the latest file ({max_date_file}):")
# print(json.dumps(content, indent=4))

# test.py
from elo_analysis import return_full_category_table
from generate_arena_tabl import generate_arena_leaderboard_json

if __name__ == "__main__":
    generate_arena_leaderboard_json()
