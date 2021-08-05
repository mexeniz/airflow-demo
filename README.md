# airflow-demo
A showcase repository for Apache Airflow. The docker images of Airflow and instructions are based on https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html. In addition, an example DAG of KNN model training is provided for demonstration of XCOM feature and DAG parameters.

## 1 Installation

### 1.1 Requirement
- `docker-compose`: v1.27.0+

### 1.2 Set up environment variables
1. Create `.env` file. Environment varibles in this file will be used in `docker-compose.yaml`. After that, set a path to `data` folder with your external folder.
```
AIRFLOW_HOST_DATA_PATH="./data"
```
2. Generate a fernet key by Python (Ref [link](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/fernet.html#generating-fernet-key)).
```
from cryptography.fernet import Fernet
fernet_key= Fernet.generate_key()
print(fernet_key.decode())
```
3. Put a key into `.env`. This key is required to persist Variables set in Airflow.
```
AIRFLOW_FERNET_KEY="YOUR_KEY"
```
4. Add these new variables about user and group IDs.
```
echo -e "\nAIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" >> .env
```
5. Finally, your `.env` file should look like this:
```
AIRFLOW_HOST_DATA_PATH="./data"
AIRFLOW_FERNET_KEY="YOUR_KEY"
AIRFLOW_UID=1000
AIRFLOW_GID=0
```

### 1.3 Initialize and Run
1. (Optional) Edit some env variables of `x-airflow-common` in `docker-compose.yaml`. For example, you might want to load default example DAGs (~20 DAGs). Then, just set `AIRFLOW__CORE__LOAD_EXAMPLES` to `'true'`.
```
x-airflow-common:
  &airflow-common
  build:
    context: .
    dockerfile: docker/airflow/Dockerfile
    args:
        # The default Airflow base image is "apache/airflow:2.1.2-python3.9".
        - AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME:-apache/airflow:2.1.2-python3.9}
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    AIRFLOW__CORE__FERNET_KEY: "${AIRFLOW_FERNET_KEY:-}"
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'true'
```
2. **NOTE:** These folders should be manually created. Otherwise, they will be automatically created and owned by `root`.
```
mkdir ./dags ./logs ./plugins ./data
docker-compose up airflow-init
```
3. Now, a related database is set up. Let's spin up Airflow instances
```
docker-compose up -d
```
4. Airflow server is accessible at `http://localhost:8080`. Username and password are `airflow`.

## 2 DAG
### 2.1 Training KNN Model
![Alt text](./screenshots/dag_train_knn_model.png?raw=true)