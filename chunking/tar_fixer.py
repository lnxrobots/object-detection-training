import os
import sys
import tarfile
import shutil

def fix_tar(filename):
    print(f'Extracting {filename}')
    dir = filename+'_extracted'
    with tarfile.open(filename, 'r') as tar:
        try:
            tar.extractall(path=dir)
        except tarfile.ReadError:
            pass

    numbers = []
    for file in os.listdir(dir):
        if file.endswith('.jpg'):
            numbers.append(int(file.split('.')[0][5:]))

    print(f'Removing frame{max(numbers)}.jpg')
    os.remove(os.path.join(dir, f'frame{max(numbers)}.jpg'))

    print(f'Creating {filename}.temp')
    with tarfile.open(filename+'.temp', 'w') as tar:
        tar.add(dir, arcname='.')

    print(f'Replacing {filename}')
    os.replace(filename+'.temp', filename)
    print(f'Removing {dir}')
    shutil.rmtree(dir)

if __name__ == "__main__":
    filename = sys.argv[1]
    fix_tar(filename)
