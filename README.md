# airflow-demo
A showcase repository for Apache Airflow. The docker images of Airflow are based on https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html. One DAG example of KNN model training is provided for demonstration of XCOM feature and DAG parameters.

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

### 1.3 Initialize and Run
1. **NOTE:** These folders should be manually created. Otherwise, they will be automatically created and owned by `root`.
```
mkdir ./dags ./logs ./plugins ./data
docker-compose up airflow-init
```
2. Now, a related database is set up. Let's spin up Airflow instances
```
docker-compose up -d
```
3. Airflow server is accessible at `http://localhost:8080`