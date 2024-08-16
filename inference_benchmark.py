import os
import cv2
import time
import ultralytics

# Path to the directory containing the test images
image_dir = "test_images"

# Get a list of all jpg files in the directory
image_files = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]

# Create an empty list to store the image arrays
image_array_list = []

# Load each image as a numpy array and append it to the list
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    image = cv2.imread(image_path)
    image_array_list.append(image)

# Load the YOLO model
model = ultralytics.YOLO('training_results/result_test3_ball_smudge_limited_augmentation/runs/detect/train6/weights/test3_ball_smudge_limited_augmentation.pt')

# Perform YOLO prediction on each image and measure the time
start_time = time.perf_counter()

for image_array in image_array_list:
    model.predict(image_array)

end_time = time.perf_counter()
execution_time = end_time - start_time
time_of_frame = execution_time / len(image_array_list)
fps = 1 / time_of_frame

# Print the execution time
print(f"Frame time: {time_of_frame*1000:.2f} ms, {fps:.2f} fps")
