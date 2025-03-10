import sqlite3
import os
import sys
import json
import tarfile
import cv2
import re
import numpy as np
import hashlib
from datetime import datetime
from database_tools.replay_parsers import parse_lnxrepl
from constants import *

# Configuration
START_REL_PATH = sys.argv[1]

START_PATH = os.path.join(FRAMES_ROOT, START_REL_PATH)

INSERT_ROW = 'INSERT INTO frames ({}) VALUES ({});'

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

os.makedirs(ALL_FRAMES_PATH, exist_ok=True)

# Step 1: Create SQLite database and table
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open("create_table.sql") as f:
    cursor.execute(f.read())

conn.commit()


for root, dirs, files in os.walk(START_PATH):
    for file in files:
        tar_path = os.path.join(root, file)
        if not tar_path.endswith("Front.tar"):
            continue
        # continue if there is the same tar file in the database
        rel_tar_path = os.path.normpath(os.path.relpath(tar_path, FRAMES_ROOT))
        cursor.execute('SELECT * FROM frames WHERE orig_tar_path = ?', (rel_tar_path,))
        if cursor.fetchone() is not None:
            print(f"Skipping {tar_path}")
            continue

        replay = find_replay(root, file)
        entries = {}

        if replay is not None:
            with open(replay) as f:
                for line in f:
                    data = parse_lnxrepl(line)
                    if data is None:
                        continue
                    data["front_frame_ID"] += REPLAY_FRAME_OFFSET
                    if data["front_frame_ID"] not in entries:
                        entries[data["front_frame_ID"]] = data

        with tarfile.open(tar_path) as tar:
            members = tar.getmembers()
            for mi, member in enumerate(members):
                if not member.name.endswith(".jpg"):
                    continue

                frame_num = int(os.path.split(member.name)[1].replace('.jpg', '').replace('frame', ''))

                with tar.extractfile(member) as f:
                    data = f.read()
                    img_hash = hashlib.md5(data).hexdigest()
                    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                    hue_avg = np.mean(hsv[:,:,0])
                    hue_std = np.std(hsv[:,:,0])
                    sat_avg = np.mean(hsv[:,:,1])
                    val_avg = np.mean(hsv[:,:,2])

                member.name = f'{cursor.lastrowid+1:07}.jpg'
                tar.extract(member, path=ALL_FRAMES_PATH)

                # print(tar_path, rel_tar_path)
                new_data = {
                    "orig_tar_path": rel_tar_path,
                    "orig_frame_num": frame_num,
                    "hue_avg": hue_avg,
                    "hue_std": hue_std,
                    "sat_avg": sat_avg,
                    "val_avg": val_avg,
                    "md5": img_hash,
                    "chosen": False,
                    "has_annotation": False
                }

                if frame_num in entries:
                    data = entries[frame_num]
                    new_data.update({
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
                    })
                    for obj in ['ball', 'goal']:
                        for i, coord in enumerate(['x', 'y', 'w', 'h']):
                            new_data[f'{obj}_{coord}'] = data[f'front_{obj}_bb'][i]

                if mi % 200 == 0:
                    print('\r'+progress_bar(mi/len(members)), end='')
                command = INSERT_ROW.format(str(list(new_data.keys()))[1:-1], str(list(new_data.values()))[1:-1])
                # print(command)
                cursor.execute(command, new_data)
        conn.commit()
        print(end='\r')
        print(f"Processed {tar_path} (last ID: {cursor.lastrowid})")

conn.close()
