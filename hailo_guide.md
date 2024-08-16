# Guide for Hailo 8l

TODO: find out whether `.pt` not from docker works.

## Hailo software

https://hailo.ai/developer-zone/software-downloads/

*Hailo AI Software Suite - Self Extractable* worked fine. Download the same version as in Raspberry Pi repos.

For installation, remove `linux-headers...` from requirements and comment out installation of pcie drivers.

## Training

[Training in docker](https://github.com/hailo-ai/hailo_model_zoo/tree/833ae6175c06dbd6c3fc8faeb23659c9efaa2dbe/training/yolov8) worked, not sure if normal training works

```
yolo detect train data=object_detection_test1_2chunks/data.yaml pretrained=0 epochs=200 mosaic=0 translate=0 degrees=0 scale=0 shear=0 perspective=0 crop_fraction=0 batch=16
```

## Export ONNX and compile

https://github.com/hailo-ai/hailo-rpi5-examples/blob/main/doc/retraining-example.md

### Export

```
yolo export model=hailo_test3.pt imgsz=640 format=onnx opset=11
```

### Compile

Add some images to test_images, for optimalization. `.alls` and `.json` in `hailo_compilation_files`.

```
hailomz compile yolov8n --ckpt=hailo_test3.onnx --hw-arch hailo8l --calib-path test_images/ --classes 2 --model-script yolov8n.alls
```

## Raspberry Pi preparation

https://www.raspberrypi.com/documentation/accessories/ai-kit.html

### Custom software

https://community.hailo.ai/t/still-unable-to-run-4-18-on-rpi5/1985/14

Use with caution, didn't really work.

## Raspberry Pi inference

https://github.com/hailo-ai/hailo-rpi5-examples/blob/main/README.md

For raspberry pi camera, modify autofocus mode as the error says and add framerates everywhere where is size set in `basic_pipelines/detection.py`
