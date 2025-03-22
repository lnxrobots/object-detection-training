import os
import sys
import tarfile
import cv2
import numpy as np
import json
# from tar_fixer import fix_tar
from replay_parsers import parse_lnxrepl
from datetime import datetime

directory = sys.argv[1]
frames_dir = os.path.join(directory, 'frames')
replays_dir = os.path.join(directory, 'replays')
output_dir = os.path.join(directory, 'output')
done_file = os.path.join(directory, 'done.json')
scale = 2.4
suffix = "Front"

def add_bounding_box(img, position, color):
    ih, iw = img.shape[:2]
    x, y, w, h = position
    return cv2.rectangle(img, (int((x-w/2)*iw), int((y-h/2)*ih)), (int((x+w/2)*iw), (int((y+h/2)*ih))), color, 2)

def display_frame(img, orig_img, frame_num, file):
    cv2.imshow('frame', img)
    cv2.setWindowTitle('frame', f'{file} - Frame {frame_num}')
    key = cv2.waitKey(0)
    if key in [ord('p'), ord('s')]:  # If 'p' key is pressed
        output_path = os.path.join(output_dir, f'{file}_frame{frame_num}.jpg')
        cv2.imwrite(output_path, orig_img)
        print(f"Saved {output_path}")
    elif key in [ord('q'), -1]:  # If 'q' key is pressed
        sys.exit(0)
    return key

def save_done(file, i):
    global done_frames
    done_frames[file] = i
    with open(done_file, 'w') as f:
        json.dump(done_frames, f)

os.makedirs(output_dir, exist_ok=True)

done_frames = {}
if os.path.exists(done_file):
    with open(done_file) as f:
        done_frames = json.load(f)

for file in os.listdir(frames_dir):
    tar_path = os.path.join(frames_dir, file)
    if not file.endswith(suffix+'.tar'):
        continue

    members = []
    try:
        with tarfile.open(tar_path) as tar:
            members = tar.getmembers()
    except tarfile.ReadError:
        # print(f"\nFixing {tar_path}", end='\n\n')
        # fix_tar(tar_path)
        # print('')
        print(f"Invalid tar file: {tar_path}")
        continue

    # Extract date and time from the tar file name
    tar_datetime = datetime.strptime(file, f'frames_%Y-%m-%d-%H_%M_%S_{suffix}.tar')

    # Find the matching replay file
    for replay_file in os.listdir(replays_dir):
        replay_datetime = datetime.strptime(replay_file, 'replay_%Y-%m-%d-%H_%M_%S.lnxrepl')

        # Check if the time difference is within 1 second
        if abs((tar_datetime - replay_datetime).total_seconds()) <= 1:
            replay_path = os.path.join(replays_dir, replay_file)
            break
    else:
        print(f"No matching replay file found for {tar_path}")
        continue

    frame_data = {}
    with open(replay_path, 'r') as replay:
        for line in replay:
            data = parse_lnxrepl(line)
            if data:
                num = data['front_frame_ID']
                if num not in frame_data:
                    frame_data[num] = data

    with tarfile.open(tar_path) as tar:
        try:
            frame_numbers = sorted([int(member.name.replace('.jpg', '').replace('frame', '')) for member in members])
        except ValueError:
            print(f"Invalid frame number in {file} ({tar_path})")
            continue
        if file in done_frames and done_frames[file] >= len(frame_numbers):
            continue
        current_frame_index = done_frames.get(file, 0)

        while current_frame_index < len(frame_numbers):
            frame_num = frame_numbers[current_frame_index]
            done_frames[file] = current_frame_index

            if frame_num not in frame_data:
                print(f"Frame {frame_num} not found in replay file")
                current_frame_index += 1
                save_done(file, current_frame_index)
                continue
            save_done(file, current_frame_index)

            data = frame_data[frame_num]
            orig_img = cv2.imdecode(np.frombuffer(tar.extractfile(members[current_frame_index]).read(), np.uint8), cv2.IMREAD_COLOR)
            img = cv2.resize(orig_img, (int(orig_img.shape[1]*scale), int(orig_img.shape[0]*scale)))
            img = add_bounding_box(img, data['front_ball_bb'], (255, 0, 0))

            key = display_frame(img, orig_img, frame_num, file)
            if key == ord('a'):  # Left arrow key
                current_frame_index = max(0, current_frame_index - 1)
            elif key == ord('d'):  # Right arrow key
                current_frame_index += 1
