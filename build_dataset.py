import os
import sys
import zipfile
import tarfile
import shutil

from json_to_yolo import json_to_yolo
from split_dataset import split_dataset

if len(sys.argv) < 2:
    print('Usage: python build_dataset.py <dataset_name> [class1=0 ... classN=n] [split=[train_ratio,val_ratio]]')
    sys.exit(1)

LABEL_CHUNKS_DIR = 'label_chunks'
FRAME_CHUNKS_DIR = 'frame_chunks'
DATASET_DIR = os.path.join('datasets', sys.argv[1])
CLASSES = {}
SPLIT_RATIOS = None
for arg in sys.argv[2:]:
    key, value = arg.split('=')
    if key == 'split':
        SPLIT_RATIOS = [float(ratio) for ratio in value.strip('[]').split(',')]
    else:
        CLASSES[key] = int(value)

CLASSES_DEDUP = ['' for _ in range(max(set(CLASSES.values()))+1)]
for key, value in CLASSES.items():
    if not CLASSES_DEDUP[int(value)]:
        CLASSES_DEDUP[int(value)] = key

shutil.rmtree(DATASET_DIR)
os.makedirs(DATASET_DIR, exist_ok=True)
for dir in ['images', 'labels', 'labels_json']:
    os.makedirs(os.path.join(DATASET_DIR, dir), exist_ok=True)

# Extract label chunks
chunk_names = []
for chunk in os.listdir(LABEL_CHUNKS_DIR):
    chunk_names.append(os.path.splitext(chunk)[0])
    print(f'Extracting labels from {chunk}...')
    with zipfile.ZipFile(os.path.join(LABEL_CHUNKS_DIR, chunk), 'r') as zip_ref:
        zip_ref.extractall(os.path.join(DATASET_DIR, 'labels_json'))

# Extract frame chunks
for path, dirs, files in os.walk(FRAME_CHUNKS_DIR):
    for file in files:
        name, ext = os.path.splitext(file)
        if not (ext == '.tar' and name in chunk_names):
            continue
        print(f'Extracting frames from {file}...')
        with tarfile.open(os.path.join(path, file), 'r') as tar_ref:
            tar_ref.extractall(os.path.join(DATASET_DIR, 'images'))

print('Converting JSON labels to YOLO format...')
json_to_yolo(os.path.join(DATASET_DIR, 'labels_json'), os.path.join(DATASET_DIR, 'labels'), CLASSES)

print('Creating empty label files for images without labels...')
for img in os.listdir(os.path.join(DATASET_DIR, 'images')):
    name = os.path.splitext(img)[0]
    filename = os.path.join(DATASET_DIR, 'labels', f'{name}.txt')
    if not os.path.isfile(filename):
        file = open(filename, 'w')
        file.close()

print('Splitting dataset...')
if SPLIT_RATIOS is not None:
    split_dataset(DATASET_DIR, os.path.join(DATASET_DIR, 'images'), os.path.join(DATASET_DIR, 'labels'))

print('Cleaning up...')
for path, dirs, files in os.walk(DATASET_DIR):
    if not files:
        try:
            os.rmdir(path)
        except OSError:
            pass

print('Dataset successfully built!')
