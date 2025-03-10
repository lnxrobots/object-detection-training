import os
import sys
import shutil

from json_to_yolo import json_to_yolo
from split_dataset import split_dataset
from constants import *

if len(sys.argv) < 2:
    print('Usage: python build_dataset.py <dataset_name> [class1=0 ... classN=n] [split=[train_ratio,val_ratio]]')
    sys.exit(1)

DATASET_DIR = os.path.join(DATASETS_DIR, sys.argv[1])

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

os.makedirs(DATASET_DIR, exist_ok=True)
shutil.rmtree(DATASET_DIR)
os.makedirs(DATASET_DIR, exist_ok=True)
for dir in ['images', 'labels', 'labels_json']:
    os.makedirs(os.path.join(DATASET_DIR, dir), exist_ok=True)


print('Copying labeling files and images to dataset directory...')
for file in os.listdir(LABELING_PATH):
    if file.endswith('.json'):
        dest = os.path.join(DATASET_DIR, 'labels_json')
    elif file.endswith('.jpg'):
        dest = os.path.join(DATASET_DIR, 'images')
    else:
        continue
    shutil.copy(os.path.join(LABELING_PATH, file), dest)

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
    split_dataset(DATASET_DIR, os.path.join(DATASET_DIR, 'images'), os.path.join(DATASET_DIR, 'labels'), *SPLIT_RATIOS)

print('Cleaning up...')
for path, dirs, files in os.walk(DATASET_DIR):
    if not files:
        try:
            os.rmdir(path)
        except OSError:
            pass

print('Dataset successfully built!')
