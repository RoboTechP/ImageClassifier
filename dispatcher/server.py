from flask import Flask, request, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import io
import logging

app = Flask(__name__)

# Prometheus metrics
TOTAL_RECEIVED_REQUESTS = Counter('http_requests', 'Total number of received HTTP requests', ['endpoint'])

# Wrap your app with the Prometheus WSGI middleware
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.before_request
def before_request():
    TOTAL_RECEIVED_REQUESTS.labels(endpoint=request.endpoint).inc()
    app.logger.info(f"Incrementing counter for {request.endpoint} endpoint.")

@app.route('/')
def home():
    return "<h1> Welcome From Classification Server </h1>"

# Loads pre-trained model here and move it to CPU
device = torch.device('cpu')
model = models.resnet50()
model.load_state_dict(torch.load('resnet50.pth', map_location=device))
model.to(device)
model.eval()

# Load ImageNet class labels
with open('imagenet1000_clsidx_to_labels.txt') as f:
    class_names = eval(f.read())

def process_image(file):
    try:
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        img_t = preprocess(img)
        batch_t = torch.unsqueeze(img_t, 0)
        
        with torch.no_grad():
            out = model(batch_t.to(device))
        probabilities = torch.nn.functional.softmax(out[0], dim=0)
        top_prob, top_catid = torch.topk(probabilities, 1)
        
        result = {
            'class': class_names[top_catid[0].item()],
            'probability': f'{top_prob[0].item() * 100:.2f}%'
        }
        return result
    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return {'error': str(e)}

@app.route('/classify', methods=['POST'])
def classify():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    result = process_image(file)
    return jsonify(result), 200

@app.route('/total_requests', methods=['GET'])
def total_requests():
    all_metrics = {}
    for label_value_tuple in TOTAL_RECEIVED_REQUESTS.collect()[0].samples:
        all_metrics[label_value_tuple.labels['endpoint']] = label_value_tuple.value
    return jsonify(all_metrics)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)
