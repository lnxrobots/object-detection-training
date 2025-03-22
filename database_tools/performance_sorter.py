import os
import sys
import cv2

def main(image_dir, output_file):
    # Get list of jpg files in the directory
    images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    images.sort()  # Sort images alphabetically
    if not images:
        print("No images found in the directory.")
        return

    current_index = 0
    window_name = "Image Viewer"

    # Create a resizable window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        # Load the current image
        image_path = os.path.join(image_dir, images[current_index])
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            break

        # Get the current window size
        def resize_and_display_image():
            height, width = image.shape[:2]
            window_width = cv2.getWindowImageRect(window_name)[2]
            window_height = cv2.getWindowImageRect(window_name)[3]
            scale_factor = min(window_width / width, window_height / height)
            scaled_image = cv2.resize(image, (int(width * scale_factor), int(height * scale_factor)))
            cv2.imshow(window_name, scaled_image)

        resize_and_display_image()

        # Wait for key press
        key = cv2.waitKey(0)

        if key == ord('w'):  # Scroll to the previous image
            current_index = (current_index - 1) % len(images)
        elif key == ord('d'):  # Scroll to the next image
            current_index = (current_index + 1) % len(images)
        elif key == ord('s'):  # Save the current filename
            with open(output_file, 'a') as f:
                print(images[current_index].replace('.jpg', ''), file=f)
            print(f"Saved: {images[current_index]}")
        elif key == 27:  # ESC key to exit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_directory = sys.argv[1]  # Replace with your directory path
    output_txt = sys.argv[2] if len(sys.argv) > 2 else "saved_filenames.txt"  # Replace with your desired output file
    main(image_directory, output_txt)
