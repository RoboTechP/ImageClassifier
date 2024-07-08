import requests
import time
import os

# Configuration
ENDPOINT = 'http://192.168.49.2:32000/classify'  # Use the NodePort from `kubectl get svc dispatcher-service`
IMAGE_DIR = './images/'  # Relative path to the directory containing images to send

# Workload configuration
workload = [14, 12, 14, 13, 14, 17, 15, 15, 14, 17, 13, 19, 18, 15, 14, 18, 14, 15, 16, 16, 17, 15, 13, 15, 11, 15, 17, 20, 14, 11, 16, 14, 16, 13, 17, 12, 14, 16, 13, 17, 14, 15, 13, 12, 13, 14, 16, 13, 12, 13, 12, 11, 14, 15, 14, 17, 16, 16, 12, 11, 18, 12, 14, 13, 15, 14, 13, 17, 16, 16, 11, 16, 16, 14, 12, 11, 17, 12, 9, 11, 15, 13, 13, 14, 13, 14, 11, 13, 13, 13, 13, 17, 12, 14, 15, 17, 13, 13, 10, 15, 14, 15, 16, 17, 15, 11, 14, 13, 12, 13, 13, 17, 15, 14, 17, 17, 13, 14, 17, 15, 20, 13, 17, 14, 16, 13, 12, 14, 15, 19, 12, 15, 19, 16, 14, 14, 16, 12, 11, 13, 16, 15, 16, 12, 15, 12, 17, 13, 12, 19, 13, 18, 16, 19, 15, 12, 18, 17, 16, 21, 15, 16, 14, 13, 17, 14, 10, 12, 13, 13, 14, 14, 17, 12, 14, 10, 14, 12, 18, 12, 13, 14, 19, 11, 21, 12, 13, 16, 11, 10, 16, 16, 15, 12, 13, 18, 16, 17, 19, 14, 20, 17, 12, 16, 16, 12, 13, 14, 10, 14, 21, 19, 13, 16, 16, 10, 16, 19, 17, 17, 15, 16, 19, 13, 17, 15, 14, 15, 17, 15, 19, 20, 13, 15, 16, 14, 15, 16, 14, 15, 15, 14, 13, 15, 15, 14, 13, 18, 15, 13, 13, 15, 13, 16, 41, 34, 40, 56, 56, 60, 65, 63, 61, 72, 61, 65, 71, 62, 72, 62, 71, 70, 74, 76, 72, 65, 64, 72, 77, 72, 71, 88, 73, 74, 73, 75, 71, 74, 70, 77, 65, 73, 70, 67, 83, 69, 64, 72, 77, 82, 75, 84, 75, 77, 88, 73, 71, 73, 72, 71, 79, 75, 74, 75, 67, 81, 84, 77, 73, 67, 82, 86, 75, 67, 83, 85, 71, 74, 73, 71, 71, 71, 64, 77, 76, 82, 71, 71, 76, 76, 80, 77, 86, 80, 72, 82, 78, 66, 74, 71, 64, 62, 72, 68, 61, 65, 65, 65, 61, 71, 68, 63, 61, 66, 75, 61, 60, 69, 63, 69, 67, 69, 64, 67, 72, 66, 59, 64, 66, 68, 74, 68, 74, 62, 66, 65, 74, 67, 66, 72, 77, 72, 64, 68, 69, 65, 70, 71, 78, 64, 70, 78, 62, 72, 76, 74, 68, 72, 75, 67, 70, 69, 67, 70, 68, 63, 66, 66, 59, 51, 54, 57, 56, 50, 53, 60, 56, 56, 65, 59, 56, 48, 55, 45, 49, 54, 40, 37, 41, 43, 34, 41, 38, 39, 39, 35, 41, 36, 37, 40, 39, 37, 41, 44, 33, 39, 33, 29, 27, 30, 24, 36, 39, 41, 42, 39, 37, 36, 36, 29, 32, 28, 30, 28, 24, 24, 27, 25, 25, 28, 27, 23, 22, 20, 15, 15, 23, 18, 18, 13, 15, 16, 16, 16, 16, 13, 17, 18, 15, 13, 14, 19, 18, 16, 16, 15, 22, 16, 15, 16, 13, 16, 14, 18, 19, 15, 14, 15, 15, 20, 13, 18, 15, 15, 15, 16, 18, 15, 20, 14, 12, 15, 14, 12, 12, 18, 16, 16, 12, 15, 21, 16, 20, 15, 14, 15, 18, 14, 17, 13, 10, 15, 14, 17, 15, 14, 16, 18, 11, 17, 17, 14, 17, 17, 19, 17, 18, 16, 19, 18, 16, 17, 17, 17, 16, 18, 15, 16, 18, 15, 15, 13, 12, 16, 20, 16, 16, 15, 15, 14, 21, 11, 16, 12, 13, 17, 15, 15, 17, 17, 18, 19, 14, 15, 16, 19, 19, 16, 20, 16, 17, 11, 20, 14, 18, 18, 14, 21, 15, 12, 17, 23, 17, 14, 16, 18, 13, 14, 15, 17]



def send_request(endpoint, image_path):
    url = endpoint
    files = {'file': open(image_path, 'rb')}
    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            try:
                print(response.json())
            except ValueError:
                print(f"Non-JSON response received: {response.text}")
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def load_test(endpoint, num_requests, image_dir, start_index):
    print(f"Current working directory: {os.getcwd()}")
    print(f"Listing all files in the directory: {image_dir}")
    
    if not os.path.isdir(image_dir):
        print("Error: The specified image directory does not exist or is not a directory.")
        return
    
    all_files = os.listdir(image_dir)
    images = [os.path.join(image_dir, img) for img in all_files if img.lower().endswith(('.jpeg', '.jpg', '.png'))]
    print(f"Found {len(images)} images:")
    
    if not images:
        print("Error: No images found in the specified directory.")
        return

    for i in range(num_requests):
        image_path = images[(start_index + i) % len(images)]
        send_request(endpoint, image_path)

if __name__ == "__main__":
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: Image directory {IMAGE_DIR} does not exist.")
    else:
        start_index = 0
        for index, num_requests in enumerate(workload):
            print(f"Starting load test with {num_requests} requests (Batch {index + 1})")
            load_test(ENDPOINT, num_requests, IMAGE_DIR, start_index)  # Send specified number of requests in the current batch
            start_index += num_requests  # Update the start index for the next batch
            print(f"Completed batch {index + 1}. Moving towards batch {index + 2}...\n")
            time.sleep(1)  # Short sleep to separate each load test phase

        print("Load test completed for all batches.")
