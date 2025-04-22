# Guide for Hailo 8l

## Dataset building

```
python build_dataset.py front_ball_6552 ball=0 smudge=1 split=[0.8,0.15]
```

## Hailo software

https://hailo.ai/developer-zone/software-downloads/

*Hailo AI Software Suite - Self Extractable* worked fine. Download the same version as in Raspberry Pi repos.

For installation, remove `linux-headers...` from requirements and comment out installation of pcie drivers.

## Training

[Training in docker](https://github.com/hailo-ai/hailo_model_zoo/tree/833ae6175c06dbd6c3fc8faeb23659c9efaa2dbe/training/yolov8) worked, classic one didn't

```
docker run --name "my_yolo_training" -it --gpus all --ipc=host -v ./datasets/:/workspace/ultralytics/datasets/ -v ./results/:/workspace/ultralytics/results/ yolov8:v0
```

```
yolo detect train data=datasets/test2_5chunks/data.yaml pretrained=0 epochs=200 mosaic=0 translate=0 degrees=0 scale=0 shear=0 perspective=0 batch=16
```

## Export ONNX and compile

https://github.com/hailo-ai/hailo-rpi5-examples/blob/main/doc/retraining-example.md

### Export

```
yolo export model=best.pt imgsz=640 format=onnx opset=11
```

### Compile

Add some images to test_images, for optimalization. `.alls` and `.json` in `hailo_compilation_files`.

```
hailomz compile yolov8n --ckpt=hailo_test3.onnx --hw-arch hailo8l --calib-path test_images/ --classes 2 --model-script yolov8n.alls
```

## Raspberry Pi preparation

https://www.raspberrypi.com/documentation/accessories/ai-kit.html

### Custom software

For installation of latest hailo software

https://community.hailo.ai/t/still-unable-to-run-4-18-on-rpi5/1985/14

Not recommended, didn't really work.

## Raspberry Pi inference

Using built-in picamera2 interface. Accepts BGR input (the channels in the example are in the wrong order)

https://github.com/raspberrypi/picamera2/blob/main/examples/hailo/detect.py

