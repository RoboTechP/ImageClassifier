import time
import requests
from kubernetes import client, config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROMETHEUS_URL = "http://localhost:9090"
DEPLOYMENT_NAME = "image-classification-deployment"
NAMESPACE = "default"

# Load Kubernetes configuration
config.load_kube_config()

def get_metric_value():
    """Fetch the number of requests in the last 20 seconds from Prometheus"""
    query = 'sum(increase(http_requests_total{service="dispatcher-service"}[20s]))'
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {'query': query}
    
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise an exception for HTTP errors
        results = response.json()['data']['result']
        if results:
            return float(results[0]['value'][1])
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching metric: {e}")
        return 0

def calculate_replicas(requests_in_last_20s, current_replicas):
    """Calculates the desired number of replicas based on requests in the last 20 seconds"""
    print(f"Requests in the last 20 seconds: {requests_in_last_20s}")
    print(f"Current replicas: {current_replicas}")

    if current_replicas == 1 and requests_in_last_20s > 20:
        return 2
    elif current_replicas == 2 and requests_in_last_20s > 120:
        return 3
    elif current_replicas == 3 and requests_in_last_20s > 300:
        return 4
    elif current_replicas > 2 and requests_in_last_20s < 40:
        return 2
    elif current_replicas == 2 and requests_in_last_20s < 20:
        return 2
    else:
        return current_replicas
    """Calculate the desired number of replicas based on requests in the last 20 seconds"""
    print(f"Requests in the last 20 seconds: {requests_in_last_20s}")
    print(f"Current replicas: {current_replicas}")

    if current_replicas == 1 and requests_in_last_20s > 20:
        return 2
    elif current_replicas == 2 and requests_in_last_20s > 120:
        return 3
    elif current_replicas == 3 and requests_in_last_20s > 300:
        return 4
    elif current_replicas > 1 and requests_in_last_20s < 40:
        return 2
    else:
        return current_replicas

def update_replicas(deployment_name, namespace, replicas):
    """Update the number of replicas in the Kubernetes deployment"""
    api_instance = client.AppsV1Api()
    body = {
        'spec': {
            'replicas': replicas
        }
    }
    api_instance.patch_namespaced_deployment_scale(deployment_name, namespace, body)

def get_current_replicas(deployment_name, namespace):
    """Get the current number of replicas in the Kubernetes deployment"""
    api_instance = client.AppsV1Api()
    deployment = api_instance.read_namespaced_deployment_scale(deployment_name, namespace)
    return deployment.spec.replicas

def main():
    """Main autoscaling loop"""
    while True:
        try:
            # Fetch the latest requests in the last 20 seconds value
            requests_in_last_20s = get_metric_value()

            # Get current number of replicas
            current_replicas = get_current_replicas(DEPLOYMENT_NAME, NAMESPACE)

            # Calculate desired replicas based on requests in the last 20 seconds
            desired_replicas = calculate_replicas(requests_in_last_20s, current_replicas)

            # Update deployment replicas if needed
            if desired_replicas != current_replicas:
                print(f"Updating replicas from {current_replicas} to {desired_replicas}")
                update_replicas(DEPLOYMENT_NAME, NAMESPACE, desired_replicas)
            else:
                print("No change in replicas needed")

        except Exception as e:
            print(f"Error: {e}")
        
        # Sleep for 20 seconds
        time.sleep(20)

if __name__ == "__main__":
    main()
