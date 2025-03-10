import sqlite3
import os
import json
import re
from datetime import datetime
from database_tools.replay_parsers import parse_lnxrepl
from constants import *

def has_same_time(tar_name, repl_name):
    tar_datetime = re.search(r'\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_\d{2}', tar_name).group(0)
    repl_datetime = re.search(r'\d{4}-\d{2}-\d{2}-\d{2}_\d{2}_\d{2}', repl_name).group(0)

    tar_datetime = datetime.strptime(tar_datetime, '%Y-%m-%d-%H_%M_%S')
    repl_datetime = datetime.strptime(repl_datetime, '%Y-%m-%d-%H_%M_%S')
    return abs((tar_datetime - repl_datetime).total_seconds()) <= 1

def find_replay(tar_root, tar_name):
    tar_root = tar_root.rstrip('/')  # Remove trailing slash if present
    visited_dirs = set()
    for _ in range(3):
        for root, _, files in os.walk(tar_root):
            if root in visited_dirs:
                continue
            visited_dirs.add(root)
            for file in files:
                if file.endswith('.lnxrepl') and has_same_time(tar_name, file):
                    return os.path.join(root, file)
        tar_root = os.path.dirname(tar_root)
    return None

def progress_bar(progress, length=50):
    return f'|{"█"*int(progress*length)}{" "*(length-int(progress*length))}| {progress*100:.2f} %'


# Step 1: Create SQLite database and table
conn = sqlite3.connect(DB_PATH)

entry_dict = {}

for i, row in enumerate(conn.execute('SELECT id, orig_tar_path, orig_frame_num FROM frames WHERE orig_entry_id IS NULL')):
    fr_id, tar_path, frame_num = row
    root, file = os.path.split(tar_path)
    root = os.path.join(FRAMES_ROOT, root)

    if tar_path not in entry_dict:
        replay = find_replay(root, file)

        if replay is None:
            print(f"Replay not found for {tar_path}")
            entry_dict[tar_path] = {}
            continue
        print(f"Processing {tar_path} with replay {replay}")

        entries = {}
        print("Parsing replay")
        with open(replay) as f:
            for line in f:
                data = parse_lnxrepl(line)
                if data is None:
                    continue
                data["front_frame_ID"] += REPLAY_FRAME_OFFSET
                if data["front_frame_ID"] not in entries:
                    entries[data["front_frame_ID"]] = data
        if len(entries) == 0:
            print('No entries found in replay')

        entry_dict[tar_path] = entries

    entries = entry_dict[tar_path]

    data = {}
    for offset in [0, -1, 1, -2, 2, -3, 3, -4, 4]:
        if frame_num + offset in entries:
            data = entries[frame_num + offset]
            break

    if not data:
        if entries:
            print(f"Frame {frame_num} not found in replay {replay}")
        continue

    new_data = {
        "orig_entry_id": data["entry_id"],
        "game_timestamp": data["timestamp"],
        "robot_state": data["state"],
        "line_sensors": json.dumps(data["line_sensors"]),
        "heading": data["heading"],
        "motor_values": json.dumps(data["motor_values"]),
        "robot_x": data["robot_position"][0],
        "robot_y": data["robot_position"][1],
        "robot_count": data["n_field_robots"],
        "enemy_positions": json.dumps(data["enemy_positions"])
    }
    for obj in ['ball', 'goal']:
        for i, coord in enumerate(['x', 'y', 'w', 'h']):
            new_data[f'{obj}_{coord}'] = data[f'front_{obj}_bb'][i]

    set_lines = ",".join([f"{k}=:{k}" for k in new_data.keys()])
    statement = f"UPDATE frames SET {set_lines} WHERE id={fr_id}"
    # print(statement)
    conn.execute(statement, new_data)
    if i % 100 == 0:
        conn.commit()

conn.commit()
conn.close()
