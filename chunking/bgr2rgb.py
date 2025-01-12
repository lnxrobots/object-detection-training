import os
import sys
import tarfile
import cv2
import numpy as np
from io import BytesIO

def convert_bgr_to_rgb(image_data):
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    if image is not None:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.jpg', rgb_image)
        return buffer.tobytes()
    return image_data

def process_tar_file(tar_path):
    temp_tar_path = tar_path + '.temp'
    try:
        last = None
        with tarfile.open(tar_path, 'r') as tar, tarfile.open(temp_tar_path, 'w') as temp_tar:
            members = tar.getmembers()
            for member in members:
                last = member.name
                if member.isfile() and (member.name.lower().endswith('.jpg') or member.name.lower().endswith('.jpeg')):
                    file_data = tar.extractfile(member).read()
                    rgb_data = convert_bgr_to_rgb(file_data)
                    member.size = len(rgb_data)
                    member_data = BytesIO(rgb_data)
                    temp_tar.addfile(member, member_data)
                else:
                    temp_tar.addfile(member, tar.extractfile(member))
    except tarfile.ReadError:
        print(f"Failed to process {tar_path} ({last})")
        os.remove(temp_tar_path)
        return
    os.replace(temp_tar_path, tar_path)

def main():
    directory = sys.argv[1]
    for file in os.listdir(directory):
        if file.lower().endswith('.tar'):
            process_tar_file(os.path.join(directory, file))

if __name__ == "__main__":
    main()
