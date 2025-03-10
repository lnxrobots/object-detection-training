import os
import hashlib
import sqlite3
from constants import *

conn = sqlite3.connect(DB_PATH)
# conn.execute("ALTER TABLE frames ADD COLUMN md5 TEXT")


for i, row in enumerate(conn.execute("SELECT id FROM frames WHERE md5 IS NULL")):
    num = row[0]
    file = f"{num:07}.jpg"
    print(num, end="\r")
    with open(os.path.join(ALL_FRAMES_PATH, file), "rb") as f:
        hash = hashlib.md5(f.read()).hexdigest()
    conn.execute("UPDATE frames SET md5 = ? WHERE id = ?", (hash, num))
    if i % 100 == 0:
        conn.commit()

conn.commit()
conn.close()
