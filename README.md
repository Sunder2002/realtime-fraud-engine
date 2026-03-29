# Real-Time Fraud Detection Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

An end-to-end real-time fraud detection system demonstrating advanced machine learning engineering skills, microservices architecture, and DevOps practices. This project showcases the complete lifecycle of building, deploying, and monitoring a production-ready fraud detection pipeline.

## 🚀 Overview

This system simulates a real-world fraud detection engine that processes credit card transactions in real-time. It features:

- **Data Generation**: Continuous stream of synthetic transaction data
- **Machine Learning Model**: XGBoost-based fraud classifier trained on historical data
- **Real-Time Processing**: Kafka-based event streaming for low-latency fraud detection
- **API Service**: FastAPI-powered REST API for model serving and metrics exposure
- **Monitoring & Visualization**: Prometheus metrics collection with Grafana dashboards
- **Containerized Deployment**: Docker Compose for easy local development and deployment

## 🛠 Tech Stack

- **Streaming**: Apache Kafka (with Zookeeper)
- **Machine Learning**: XGBoost, scikit-learn, pandas
- **API Framework**: FastAPI, Uvicorn
- **Serialization**: JSON over Kafka
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose
- **Programming Language**: Python 3.8+

## 🏗 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Data Generator │───▶│     Kafka       │───▶│   Fraud API     │
│   (Python)      │    │ (Transactions)  │    │  (FastAPI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Prometheus    │    │    Grafana      │
                       │   (Metrics)     │    │ (Dashboards)    │
                       └─────────────────┘    └─────────────────┘
```

### Components

1. **Data Generator** (`data_generator/`): Simulates real-time transaction streams by generating synthetic credit card transactions every 500ms and publishing them to Kafka.

2. **Model Training** (`model_training/`): Creates and trains an XGBoost classifier on dummy transaction data, saving the model for inference.

3. **Fraud Detection API** (`fraud_api/`): FastAPI application that:
   - Consumes transactions from Kafka in a background thread
   - Applies fraud detection logic (currently using a simple threshold-based rule)
   - Exposes metrics endpoint for Prometheus scraping
   - Maintains real-time counters for fraud and safe transactions

4. **Infrastructure** (`docker-compose.yml`): Containerized Kafka ecosystem with monitoring stack.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/realtime-fraud-engine.git
cd realtime-fraud-engine
```

### 2. Start Infrastructure

```bash
docker-compose up -d
```

This starts Kafka, Zookeeper, Prometheus, and Grafana.

### 3. Train the Model

```bash
cd model_training
pip install -r requirements.txt
python train.py
```

### 4. Start the Fraud Detection API

```bash
cd ../fraud_api
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Start Data Generation

```bash
cd ../data_generator
pip install -r requirements.txt
python generator.py
```

### 6. Monitor and Visualize

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **API Metrics**: http://localhost:8000/metrics

## 📊 Monitoring

The system exposes Prometheus-compatible metrics at `/metrics`:

```
# HELP total_fraud Total number of fraudulent transactions detected
# TYPE total_fraud counter
total_fraud 42

# HELP total_safe Total number of safe transactions
# TYPE total_safe counter
total_safe 1858
```

Create Grafana dashboards to visualize fraud rates, transaction volumes, and system performance.

## 🤖 Machine Learning Pipeline

### Training Phase
- Generate synthetic transaction data with fraud labels
- Feature engineering (location encoding, etc.)
- Train XGBoost classifier with optimized hyperparameters
- Model serialization using joblib

### Inference Phase
- Real-time feature extraction from Kafka messages
- Model loading and prediction
- Threshold-based fraud flagging (configurable)

## 🧪 Testing

```bash
# Run model training tests
cd model_training
python -c "import train; print('Training script loads successfully')"

# Test API endpoints
curl http://localhost:8000/metrics
```

## 📈 Performance Considerations

- **Latency**: Kafka ensures sub-second message delivery
- **Scalability**: Stateless API design allows horizontal scaling
- **Accuracy**: XGBoost provides high accuracy with fast inference
- **Monitoring**: Comprehensive metrics for production observability

## 🔧 Configuration

### Kafka Settings
- Topic: `fraud_transactions`
- Broker: `localhost:9092`
- Consumer Group: `fraud_detector`

### Model Parameters
- XGBoost: 100 estimators, max depth 6
- Fraud Threshold: Amount > $4500 (configurable)

## 🤝 Why I Built This

As a Senior Machine Learning Engineer, I created this project to demonstrate:

**End-to-End Engineering Skills**: From data generation to model deployment and monitoring, this showcases the complete ML lifecycle.

**Real-Time Systems**: Experience with event-driven architectures using Kafka for streaming data processing.

**Production-Ready Code**: Proper error handling, logging, containerization, and monitoring - all essential for production systems.

**DevOps Integration**: Docker containerization, infrastructure as code with Docker Compose, and observability with Prometheus/Grafana.

**Scalable Architecture**: Microservices design that can be independently scaled and maintained.

This project serves as a portfolio piece that proves I can design, implement, and deploy complex ML systems that handle real-world constraints like latency, scalability, and reliability.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Feel free to reach out if you have questions about the implementation or want to discuss ML engineering best practices!
