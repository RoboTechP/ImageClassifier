import requests
import time
import os
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from kubernetes import client, config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.connection import HTTPConnection
from workload import workload

# Configuration
ENDPOINT = 'http://192.168.49.2:32000/classify'
IMAGE_DIR = './images/'
PROMETHEUS_URL = "http://localhost:9090"
DEPLOYMENT_NAME = "image-classification-deployment"
NAMESPACE = "default"
THRESHOLD_UNPROCESSED_PER_POD = 40

# Increases the default socket options
HTTPConnection.default_socket_options = (
    HTTPConnection.default_socket_options + [
        (socket.SOL_SOCKET, socket.SO_SNDBUF, 50000000),  # 50MB send buffer
        (socket.SOL_SOCKET, socket.SO_RCVBUF, 50000000)   # 50MB receive buffer
    ]
)

# Loads Kubernetes configuration
config.load_kube_config()

def get_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def send_request(session, endpoint, image_path):
    url = endpoint
    files = {'file': open(image_path, 'rb')}
    try:
        response = session.post(url, files=files, timeout=60)
        response.raise_for_status()
        if response.status_code == 202:
            print("Request accepted and added to queue")
        elif response.status_code == 200:
            try:
                print(response.json())
            except ValueError:
                print(f"Non-JSON response received: {response.text}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    finally:
        files['file'].close()

def load_test(endpoint, num_requests, image_dir, start_index, concurrency_level):    
    if not os.path.isdir(image_dir):
        print("Error: The specified image directory does not exist or is not a directory.")
        return
    
    all_files = os.listdir(image_dir)
    images = [os.path.join(image_dir, img) for img in all_files if img.lower().endswith(('.jpeg', '.jpg', '.png'))]
    
    if not images:
        print("Error: No images found in the specified directory.")
        return

    with get_session() as session:
        with ThreadPoolExecutor(max_workers=concurrency_level) as executor:
            futures = []
            for i in range(num_requests):
                image_path = images[(start_index + i) % len(images)]
                futures.append(executor.submit(send_request, session, endpoint, image_path))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error in thread execution: {e}")

def get_metric_value(metric_name):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {'query': metric_name}
    
    session = get_session()
    
    try:
        response = session.get(url, params=params, timeout=30) 
        response.raise_for_status()
        results = response.json()['data']['result']
        if results:
            return float(results[0]['value'][1])
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metric: {e}")
        return 0

if __name__ == "__main__":
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: Image directory {IMAGE_DIR} does not exist.")
    else:
        start_index = 0
        for index, num_requests in enumerate(workload):
            concurrency_level = num_requests
            print(f"Starting load test with {num_requests} requests (Batch {index + 1})")
            load_test(ENDPOINT, num_requests, IMAGE_DIR, start_index, concurrency_level)
            start_index += num_requests
            print(f"Completed batch {index + 1}. Moving towards batch {index + 2}...\n")    
            time.sleep(1)

        print("Load test completed for all batches.")
