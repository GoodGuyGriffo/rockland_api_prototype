import io
import json
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request
import torch


app = Flask(__name__)
rock_class_index = json.load(open("class_labels.json"))
device = torch.device("cpu")
model = torch.load("master_model2", map_location=device)
model.eval()


def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(255),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    # tensor = tensor.cuda()
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return rock_class_index[predicted_idx]


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        class_name = get_prediction(image_bytes=img_bytes)
        return jsonify({'class_name': class_name})


if __name__ == '__main__':
    app.run()
