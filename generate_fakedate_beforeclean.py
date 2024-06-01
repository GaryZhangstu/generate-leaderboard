import json
import random
import time
from faker import Faker

# 初始化Faker库
fake = Faker()

# 定义一些常量
VOTE_TYPES = ["leftvote", "rightvote", "tievote", "bothbad_vote"]
MODEL_NAMES = ["model_a", "model_b", "model_c", "model_d"]

# 定义一个生成随机消息对话的函数
def generate_messages():
    user_messages = [
        "What is the capital of France?",
        "Tell me a joke.",
        "How do I make a cup of tea?",
        "What's the weather like today?"
    ]
    assistant_responses = [
        "The capital of France is Paris.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "To make a cup of tea, boil water, pour it over a tea bag, and let it steep for a few minutes.",
        "Today's weather is sunny with a high of 25 degrees Celsius."
    ]
    
    user_msg = random.choice(user_messages)
    assistant_msg = random.choice(assistant_responses)
    
    return [["user", user_msg], ["assistant", assistant_msg]]

# 定义一个生成随机投票数据的函数
def generate_vote_data():
    vote_data = {
        "type": random.choice(VOTE_TYPES),
        "models": random.sample(MODEL_NAMES, 2),
        "states": [
            {
                "conv_id": fake.uuid4(),
                "model_name": random.choice(MODEL_NAMES),
                "messages": generate_messages(),
                "offset": 0
            },
            {
                "conv_id": fake.uuid4(),
                "model_name": random.choice(MODEL_NAMES),
                "messages": generate_messages(),
                "offset": 0
            }
        ],
        "ip": fake.ipv4(),
        "tstamp": int(time.time())
    }
    return vote_data

# 生成指定数量的投票数据并存储在列表中
def generate_votes(num_votes):
    votes = []
    for _ in range(num_votes):
        votes.append(generate_vote_data())
    return votes

# 将列表写入文件
def write_votes_to_file(file_path, votes):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(votes, f, indent=4)

# 主函数
if __name__ == "__main__":
    file_path = "Logs/server0/server_log_20230401-1530-conv.json"  # 指定输出文件路径
    num_votes = 1000  # 指定要生成的投票数据数量

    # 生成投票数据
    votes = generate_votes(num_votes)
    
    # 将投票数据写入文件
    write_votes_to_file(file_path, votes)
    print(f"Generated {num_votes} vote data entries and wrote to {file_path}")
