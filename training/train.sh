#!/bin/bash

if [ $# -gt 1 ]; then
    nc=$2
    names=$3
else
    nc=2
    names="['ball', 'smudge']"
fi
cat <<EOF > datasets/$1/data.yaml
path: /workspace/ultralytics/datasets/$1
train: train/images
val: val/images
test: test/images
nc: $nc
names: $names
EOF

cd /workspace/ultralytics

yolo detect train data=datasets/$1/data.yaml pretrained=0 epochs=200 mosaic=0 translate=0 degrees=0 scale=0 shear=0 perspective=0 batch=16

last_folder=$(ls runs/detect/ | sort | tail -n 1)

cd runs/detect/$last_folder
yolo export model=weights/best.pt imgsz=640 format=onnx opset=11
zip -r /workspace/ultralytics/runs/$1.zip *
