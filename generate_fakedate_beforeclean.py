import json
import random
import shortuuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# List of possible models
models_list = ["model_a", "model_b", "model_c", "model_d", "model_e", "model_f"]

def generate_valid_data_entry():
    # Generate a random timestamp within the past year
    tstamp = int((datetime.now() - timedelta(days=random.randint(0, 365))).timestamp())

    # Generate random IP address
    ip = fake.ipv4()

    # Generate conversation data
    user_question = "What is the capital of France?"
    assistant_answer = "The capital of France is Paris."

    states = [
        {
            "conv_id": shortuuid.uuid(),
            "model_name": random.choice(models_list),
            "messages": [
                ["user", user_question],
                ["assistant", assistant_answer]
            ],
            "offset": 0
        },
        {
            "conv_id": shortuuid.uuid(),
            "model_name": random.choice(models_list),
            "messages": [
                ["user", user_question],
                ["assistant", assistant_answer]
            ],
            "offset": 0
        }
    ]
    anony = random.choice([True, False])
    entry = {
        "type": random.choice(["leftvote", "rightvote", "tievote", "bothbad_vote"]),
        "models": [states[0]["model_name"], states[1]["model_name"]],
        "states": states,
        "ip": ip,
        "anony": anony,
        "tstamp": tstamp
    }

    return entry

def generate_data(num_entries):
    data = []
    for _ in range(num_entries):
        data.append(generate_valid_data_entry())
    return data

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    num_entries = 1000  # Number of entries to generate
    filename = "Logs/server0/20230402-1531-conv.json"

    data = generate_data(num_entries)
    save_to_json(data, filename)

    print(f"Generated {num_entries} valid data entries and saved to {filename}")
