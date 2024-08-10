import os, sys
import zipfile

dir_path = sys.argv[1].strip('\\/ ')
export_path = os.path.join(*os.path.split(dir_path)[:-1])

name = os.path.basename(dir_path)
print('Exporting labels from', name)

zip_file_name = os.path.join(export_path, name + '.zip')
if os.path.exists(zip_file_name):
    os.remove(zip_file_name)

with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(dir_path, file_name)
            zip_file.write(file_path, file_name)
