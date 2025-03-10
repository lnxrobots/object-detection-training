import os
import json
import tarfile
import zipfile
import hashlib
import sqlite3
from constants import *

FRAME_CHUNKS = os.path.join(FRAMES_ROOT, "frame_chunks")
LABEL_CHUNKS = os.path.join(FRAMES_ROOT, "label_chunks")
LABELS_PATH = os.path.join(FRAMES_ROOT, "labeling")

conn = sqlite3.connect(DB_PATH)

for chunk in os.listdir(FRAME_CHUNKS):
    if not chunk.endswith(".tar"):
        continue
    frame_chunk = os.path.join(FRAME_CHUNKS, chunk)
    label_chunk = os.path.join(LABEL_CHUNKS, chunk.replace(".tar", ".zip"))
    print(f"Processing {chunk}")
    with tarfile.open(frame_chunk) as tar, zipfile.ZipFile(label_chunk) as zip:
        members = tar.getmembers()
        for member in members:
            with tar.extractfile(member) as f:
                md5 = hashlib.md5(f.read()).hexdigest()

            frame_id = conn.execute("SELECT id FROM frames WHERE md5=?", (md5,)).fetchone()
            if frame_id is None:
                print(f"Frame {member.name} from {chunk} not found in database")
                continue
            frame_id = frame_id[0]
            conn.execute("UPDATE frames SET has_annotation=? WHERE id=?", (True, frame_id))
            label_name = member.name.replace(".jpg", ".json")
            if label_name in zip.namelist():
                extracted_path = zip.extract(label_name, LABELS_PATH)
                with open(extracted_path, "r") as f:
                    label = json.load(f)
                label["imagePath"] = member.name
                with open(extracted_path, "w") as f:
                    json.dump(label, f)
                new_label_name = f"{frame_id:07}.json"
                new_label_path = os.path.join(LABELS_PATH, new_label_name)
                os.rename(extracted_path, new_label_path)
    conn.commit()

conn.close()
