mkdir datasets runs

# Uninstall old versions
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh

# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Build docker image
git clone https://github.com/hailo-ai/hailo_model_zoo.git --depth 1

cd hailo_model_zoo/training/yolov8
docker build --build-arg timezone=`cat /etc/timezone` -t yolov8:v0 .

# Run docker image
docker run -it --name "my_yolo_training" --gpus all --ipc=host -v ./datasets/:/workspace/ultralytics/datasets/ -v ./runs/:/workspace/ultralytics/runs/ -v ./object-detection-training/training/train.sh:/workspace/ultralytics/train.sh yolov8:v0
