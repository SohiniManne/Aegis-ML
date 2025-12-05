# 🛡️ Aegis ML: Real-Time Model Monitoring & Drift Detection System

> **A production-grade observability framework for Machine Learning models.**

![Python](https://img.shields.io/badge/Python-3.10-blue) ![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red) ![Evidently AI](https://img.shields.io/badge/AI-Evidently-orange) ![Status](https://img.shields.io/badge/Status-Active-success)

## 📌 Project Overview
In production machine learning systems, models do not crash loudly; they degrade silently. "Aegis ML" is a full-stack observability system designed to detect **Concept Drift** and **Data Integrity** issues in real-time.

It acts as a "Sidecar" to a deployed Breast Cancer Prediction model, continuously monitoring inference logs, comparing them against a training baseline using statistical tests, and triggering alerts via a live dashboard.

## 🏗️ Architecture
The system follows a decoupled Producer-Consumer pattern to ensure monitoring does not add latency to model inference.

graph LR
    A[Producer (Model Inference)] -->|Logs Events| B[(SQLite Event Store)]
    C[Scheduler] -->|Triggers| D[Drift Engine]
    B --> D
    D -->|KS-Tests & PSI| E[JSON/HTML Reports]
    E --> F[Streamlit Dashboard]
Ingestion Layer: Simulates real-time traffic and deliberately injects data corruption (drift) to test system resilience.

Detection Engine: Uses Evidently AI to run Kolmogorov-Smirnov (KS) tests on sliding windows of data.

Visualization: A real-time Streamlit dashboard that renders traffic light alerts and deep-dive statistical distributions.

📊 Key Features
Real-Time Drift Detection: Automatically flags when production data diverges statistically from training data.

Traffic Simulation: Includes a chaos-engineering script that simulates sensor failures (drift) to demonstrate system response.

Automated Scheduling: A background worker runs analysis every 10 seconds without human intervention.

Interactive Dashboard: Visualizes P95 latency, throughput, and feature distributions.

🔧 Tech Stack
Language: Python 3.10

ML & Stats: Scikit-Learn, Evidently AI, Pandas

Frontend: Streamlit

Database: SQLite (Simulating an Event Stream / Kafka)

Orchestration: Custom Python Scheduler (Simulating Airflow)

🚀 Getting Started
1. Prerequisites
Python 3.8+

pip

2. Installation
Clone the repository and install dependencies:

Bash

git clone [http://github.com/SohiniManne/Aegis-ML.git](http://github.com/SohiniManne/Aegis-ML.git)
cd aegis-ml
pip install -r requirements.txt
3. Initialization
Train the baseline model and generate the reference dataset (Gold Standard):

Bash

python src/train_model.py
🎮 How to Run the System (The "Demo Mode")
To see the full system in action, you need to run 3 separate terminals simultaneously.

Terminal 1: The Traffic Generator 🚦
This script acts as the production application. It sends data and corrupts it after 50 requests to simulate a failure.

Bash

python src/producer.py
Terminal 2: The Brain (Scheduler) 🧠
This background worker wakes up every 10 seconds to analyze the logs.

Bash

python src/scheduler.py
Terminal 3: The Dashboard 📈
This launches the web interface to visualize the health of the system.

Bash

streamlit run src/app.py
📸 Screenshots
1. System Healthy (Green)
The dashboard shows stable metrics when the producer is sending normal data.

2. Drift Detected (Red)
After ~30 seconds, the producer simulates a sensor failure. The Scheduler flags the statistical anomaly, and the dashboard turns critical.

🧠 Design Decisions & Trade-offs
SQLite vs. Kafka: For this MVP, SQLite was chosen to minimize infrastructure overhead while maintaining the "Event Log" pattern. In a high-scale environment, this would be swapped for Apache Kafka or AWS Kinesis.

Local Scheduler vs. Airflow: A custom Python loop demonstrates the logic of periodic evaluation. In production, this would be managed by Airflow DAGs or Kubeflow pipelines.

🔮 Future Roadmap
[ ] Integration with Slack/Email Webhooks for alerts.
[ ] Dockerizing the application components.
[ ] Implementing "Retraining Triggers" to automatically update the model when drift is confirmed.
