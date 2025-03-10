import os
import sqlite3
import tarfile
from constants import *

ALL_PATH = os.path.join(FRAMES_ROOT, "all/")
EXPORT_PATH = ALL_PATH

conn = sqlite3.connect(DB_PATH)
# conn.execute("ALTER TABLE frames ADD COLUMN md5 TEXT")
# conn.row_factory = sqlite3.Row

done = set(os.listdir(ALL_PATH))
print('Already exported:', len(done))

for i, row in enumerate(conn.execute("SELECT id, orig_tar_path, orig_frame_num FROM frames")):
    id, tar, num = row
    file = f"{id:07}.jpg"
    if file in done:
        continue
    print('Found', id)
    with tarfile.open(os.path.join(FRAMES_ROOT, tar)) as t:
        member = t.getmember(f"frame{num}.jpg")
        member.name = file  # Rename the member to the desired output filename
        t.extract(member, EXPORT_PATH)

conn.close()
