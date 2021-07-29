# airflow-demo
A showcase repository for Apache Airflow. The docker images of Airflow are based on https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html.

## 1 Installation

### 1.1 Requirement
- `docker-compose`: v1.27.0

### 1.2 Set up environment variables
1. Edit a path to `data` folder with your external folder.
```
AIRFLOW_DATA_PATH="./data"
```
2. Add these new variables.
```
echo -e "\nAIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" >> .env
```

### 1.3 Initialize
```
docker-compose up airflow-init
```