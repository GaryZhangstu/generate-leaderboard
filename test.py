import json
import os
import utils
from config.oss_config import upload_file



folder_path = "./tables/arena_table"
abs_path = os.path.abspath(folder_path)
max_date_file = utils.get_max_date_json_files(abs_path,"arena_table_")
if max_date_file:
    full_path = os.path.join(abs_path, max_date_file)
else:
    print('111')
content = utils.read_json_file(full_path)
print(f"Content of the latest file ({max_date_file}):")
print(json.dumps(content, indent=4))