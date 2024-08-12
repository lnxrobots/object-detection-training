import os
import json

# Create the output directory if it doesn't exist
def json_to_yolo(input_dir, output_dir, class_labels):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            with open(os.path.join(input_dir, filename)) as f:
                data = json.load(f)

            with open(os.path.join(output_dir, filename.replace('.json', '.txt')), 'w') as out_file:

                for shape in data['shapes']:

                    x1, y1 = shape['points'][0]
                    x2, y2 = shape['points'][1]

                    dw = 1./data['imageWidth']
                    dh = 1./data['imageHeight']
                    w = x2 - x1
                    h = y2 - y1
                    x = x1 + (w/2)
                    y = y1 + (h/2)

                    x *= dw
                    w *= dw
                    y *= dh
                    h *= dh

                    class_label = class_labels[shape['label']]

                    out_file.write(f"{class_label} {x} {y} {w} {h}\n")

    print("Conversion completed successfully!")
