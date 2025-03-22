import sqlite3
import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from constants import *

# Connect to DB
print("Connecting to the database...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Load frames
print("Loading frames from the database...")
query = "SELECT id, ball_x, ball_y, ball_w, ball_h, robot_x, robot_y, robot_count, hue_avg, hue_std, sat_avg, val_avg FROM frames WHERE has_annotation = 0"
df = pd.read_sql_query(query, conn)

# Handle missing values
print("Imputing missing values...")
df.fillna(df.median(), inplace=True)

# Normalize features
print("Normalizing features...")
features = df.drop(columns=["id"]).values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
features_scaled = np.array(features_scaled, dtype=np.float32)

# Run k-Means clustering
num_clusters = 2000

print(f"Running k-Means clustering with {num_clusters} clusters...")
kmeans = faiss.Kmeans(d=features_scaled.shape[1], k=num_clusters, niter=100, nredo=5, gpu=True, verbose=True)
kmeans.train(features_scaled.astype(np.float32))

# Get cluster assignments
distances, assignments = kmeans.index.search(features_scaled, 1)
df["cluster"] = assignments.flatten()

# Select one frame per cluster
print("Selecting one frame per cluster...")
chosen_frames = []
for cluster_id in range(num_clusters):
    cluster_data = df[df["cluster"] == cluster_id]
    if not cluster_data.empty:
        chosen_frames.append(cluster_data.sample(1)["id"].values[0])  # Pick one random frame per cluster

# Update database
cursor = conn.cursor()
cursor.execute("UPDATE frames SET chosen = 0")  # Reset previous selection
cursor.executemany("UPDATE frames SET chosen = 1 WHERE id = ?", [(int(i),) for i in chosen_frames])
conn.commit()
conn.close()

print(f"Selected {len(chosen_frames)} diverse frames!")
