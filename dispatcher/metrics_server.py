# metrics_server.py

from prometheus_client import start_http_server
import os

if __name__ == '__main__':
    port = int(os.environ.get('METRICS_PORT', 8000))
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}")
    
    # Keep the server running
    while True:
        pass
