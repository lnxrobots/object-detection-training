import os
import sys
import shutil
import sqlite3
from constants import *

OUTPUT = LABELING_PATH

# Connect to the database
connection = sqlite3.connect(DB_PATH)

for row in connection.execute("SELECT id FROM frames WHERE ? = 1", (sys.argv[1],)):
    f_id = row[0]
    name = f"{f_id:07}.jpg"
    shutil.copy(os.path.join(ALL_FRAMES_PATH, name), OUTPUT)

connection.close()
