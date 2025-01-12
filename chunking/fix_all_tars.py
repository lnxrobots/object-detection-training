from tar_fixer import fix_tar
import tarfile
import os
import sys

directory = sys.argv[1]

for root, dirs, files in os.walk(directory):
    for file in files:
        tar_path = os.path.join(root, file)
        if not file.endswith('.tar'):
            continue
        try:
            with tarfile.open(tar_path, 'r') as tar:
                tar.getmembers()
        except tarfile.ReadError:
            print(f"\nFixing {tar_path}", end='\n\n')
            fix_tar(tar_path)
            print('')
        else:
            print(f"{tar_path} is OK")
