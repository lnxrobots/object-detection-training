import os
import shutil

targetDirectory = "frames/temp"
robotName = "Agola"


frontDirectory = os.path.join(targetDirectory, robotName+"Front")
mirrorDirectory = os.path.join(targetDirectory, robotName+"Mirror")

os.makedirs(frontDirectory, exist_ok=True)
os.makedirs(mirrorDirectory, exist_ok=True)

"""
for folderName in os.listdir(targetDirectory):
    for replayName in os.listdir(targetDirectory + "/" + folderName + "/Jifyx"):
        for framesName in os.listdir(targetDirectory + "/" + folderName + "/Jifyx/" + replayName):
            if framesName.endswith("Mirror.tar"):
                print(framesName)
                shutil.copyfile(targetDirectory + "/" + folderName + "/Jifyx/" + replayName + "/" + framesName, "JifyxMirror/" + framesName)
"""

"""
for replayName in os.listdir(targetDirectory):
        for framesName in os.listdir(targetDirectory + "/" + replayName):
            if framesName.endswith("Mirror.tar"):
                print(framesName)
                shutil.copyfile(targetDirectory + "/" + replayName + "/" + framesName, "TestingJifyxMirror/" + framesName)
"""

for framesName in os.listdir(targetDirectory):
    if not framesName.endswith(".tar"):
        continue
    print(framesName)
    output = frontDirectory
    if framesName.endswith("Mirror.tar"):
        output = mirrorDirectory
    shutil.move(os.path.join(targetDirectory, framesName), os.path.join(output, framesName))
