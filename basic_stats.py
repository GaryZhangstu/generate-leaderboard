import os

NUM_SERVERS = 1
LOG_ROOT_DIR = "./Logs"

def get_log_files(max_num_files=None):
    # Use the provided log root directory and convert to absolute path
    log_root = os.path.abspath(LOG_ROOT_DIR)
    filenames = []

    # Iterate through the number of servers
    for i in range(NUM_SERVERS):
        server_dir = os.path.join(log_root, f"server{i}")
        # Ensure the server directory exists to avoid errors
        print(f"Checking server directory: {server_dir}")
        if not os.path.exists(server_dir):
            continue

        # List all files in the server directory
        for filename in os.listdir(server_dir):
            if filename.endswith("-conv.json"):
                print(f"Found log file: {filename}")
                filepath = os.path.join(server_dir, filename)
                name_tstamp_tuple = (filepath, os.path.getmtime(filepath))
                filenames.append(name_tstamp_tuple)

    # Sort filenames by timestamp (modification time)
    filenames = sorted(filenames, key=lambda x: x[1])

    # Extract just the file paths
    filenames = [x[0] for x in filenames]

    # Limit the number of files returned
    if max_num_files is not None:
        filenames = filenames[-max_num_files:]

    return filenames

# Example usage
log_files = get_log_files(10)
print(log_files)

