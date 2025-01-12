import os
import tarfile
import time

FIRST = 6700
PREFIX = "NameCamera"
EVENT = "Event1"
INPUT_DIR = os.path.join("frames/", PREFIX, EVENT)
OUTPUT_DIR = os.path.join('FrameChunks'+EVENT, PREFIX+"Chunks")
GROUP_SIZE = 500

NAME = EVENT+'{}.jpg'

os.makedirs(OUTPUT_DIR, exist_ok=True)
start = time.time()

frames = []
tars = []

for tarName in os.listdir(INPUT_DIR):
    print('Loading', tarName)

    tarFile = tarfile.open(os.path.join(INPUT_DIR, tarName))
    tars.append(tarFile)
    members = tarFile.getmembers()

    for m in members:
        frames.append((m, tarFile.extractfile(m)))


nGroups = len(frames) // GROUP_SIZE + 1

for i in range(nGroups):
    print(f"Creating Chunk {i+1} of {nGroups} ({(i+1)/nGroups*100:.2f} %)")
    with tarfile.open(f"{OUTPUT_DIR}/Chunk{i+FIRST}.tar", "w") as tarFile:
        for j in range(i, len(frames), nGroups):
            member, frame = frames[j]
            member.name = NAME.format(j)
            tarFile.addfile(member, frame)

print(f'Last: Chunk{nGroups-1+FIRST}.tar')

for tar in tars:
    tar.close()

t = time.time()-start
h, m, s = int(t//3600), int(t//60)%60, int(t%60)
print(f"Completed in: {h}h {m}m {s}s ({int(t)}s)")
