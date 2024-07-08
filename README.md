# ImageClassifier

ImageClassifier is a machine learning project aimed at classifying images using the ResNet50 architecture. It leverages Kubernetes for deployment and scaling, ensuring high scalability and efficiency.

The core component of this project is the Dispatcher, a Dockerized container that serves as an access point to image classification deployments. A load testing script sends images to this Dispatcher service, which then forwards requests to the appropriate deployment through load balancing.

Custom metrics are collected by Prometheus, which the monitoring component uses to enable an autoscaler. This autoscaler adjusts the number of deployments based on the incoming request load.

## Features

- **Accurate Classification**: Achieves high accuracy with the ResNet50 architecture on various image datasets.
- **Extensibility**: Easily add new models and datasets.
- **Scalable Deployment**: Dispatcher is containerized with Docker and deployed in Kubernetes for easy scaling and management.
- **Load Testing**: Simulates real-world usage by sending images to the Dispatcher service.
- **Dynamic Scaling**: Uses Prometheus to fetch custom metrics, enabling the autoscaler to dynamically adjust the number of deployments based on request load.

## Prerequisites

- Python 3.x
- minikube
- Helm
- Prometheus Community
- Virtual Environment

## Instructions

1. Clone the repository:

   ```sh
   git clone https://github.com/RoboTechP/ImageClassifier.git
   cd ImageClassifier
   ```

2. Run the model download script

   ```sh
   python downloadmodel.py
   ```

3. Apply the Kubernetes deployment:

   ```sh
   kubectl apply -f kubernetes/deployment.yaml
   ```

4. Create the Dispatcher service:

   ```sh
   kubectl apply -f kubernetes/dispatcher-service.yaml
   ```

5. Run the load tester

   ```sh
   cd loadGen
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirenments.txt
   python loadtester.py
   ```

6. Run the autoscaler  
   In the same virtual environment enabled terminal
   ```sh
   cd monitoring
   python autoscaler.py
   ```

## Project Structure

- `kubernetes/`: Contains Kubernetes configuration files
- `loadGen/`: Contains the load testing script
- `monitoring/`: Contains the autoscaler script

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License


