from datetime import datetime, timedelta
import os
from pandas.io.parsers import read_csv
import requests

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

import pandas as pd
from sklearn.model_selection  import train_test_split

DAG_NAME = "train_model"
DEFAULT_ARGS = {
    "data_url": "http://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
    "data_filename": "data.csv",
    "root_local_data_dir_path": "/data",
    "root_output_model_dir_path": "/data/models",
    "test_size": 0.3,
    "random_seed": 404
}

def prepare_local_dir_func(**kwargs):
    root_local_data_dir_path = kwargs.get("root_local_data_dir_path")

    dag_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = "{}_{}".format(kwargs["dag"].dag_id , dag_timestamp)
    local_data_dir_path = os.path.join(root_local_data_dir_path, dir_name)
    print(f"Prepare a data directory: local_data_dir_path={local_data_dir_path}")

    if not os.path.exists(local_data_dir_path):
        os.makedirs(local_data_dir_path)

    # Share setup info with other tasks
    kwargs["ti"].xcom_push(key="local_data_dir_path", value=local_data_dir_path)
    kwargs["ti"].xcom_push(key="dag_timestamp", value=dag_timestamp)

def download_data_func(**kwargs):
    data_url = kwargs.get("data_url")
    data_filename = kwargs.get("data_filename")
    local_data_dir_path =  kwargs["ti"].xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir")
    print(f"Downloading data to a local directory: url={data_url} local_data_dir_path={local_data_dir_path}")

    output_data_path = os.path.join(local_data_dir_path, data_filename)
    r = requests.get(data_url, allow_redirects=True)
    open(output_data_path, "wb").write(r.content)
    print(f"Data is downloaded: output_data_path={output_data_path}")

def preprocess_data_func(**kwargs):
    data_filename = kwargs.get("data_filename")
    test_size = kwargs.get("test_size")
    random_seed = kwargs.get("random_seed")
    local_data_dir_path =  kwargs["ti"].xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir")
    output_data_path = os.path.join(local_data_dir_path, data_filename)

    df = pd.read_csv(output_data_path)
    # Split dataframe for train and test datasets
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=random_seed)
    # Save as a file for the next task
    train_output_data_path = os.path.join(local_data_dir_path, f"train_{data_filename}")
    train_df.to_csv(train_output_data_path)
    test_output_data_path = os.path.join(local_data_dir_path, f"test_{data_filename}")
    test_df.to_csv(test_output_data_path)
    print(f"Save train and test files at {train_output_data_path} and {test_output_data_path}")

def visualize_data_func(**kwargs):
    data_filename = kwargs.get("data_filename")
    local_data_dir_path =  kwargs["ti"].xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir")
    train_output_data_path = os.path.join(local_data_dir_path, f"train_{data_filename}")
    test_output_data_path = os.path.join(local_data_dir_path, f"test_{data_filename}")
    
    # TODO(M): Replace these with actual data visualization.
    # Simply print stat of each data.
    train_df = read_csv(train_output_data_path)
    print("Show stat of a train dataset.")
    print(train_df.info())
    test_df = read_csv(test_output_data_path)
    print("Show stat of a test dataset.")
    print(test_df.info())

def train_model_func(**kwargs):
    data_filename = kwargs.get("data_filename")
    root_output_model_dir_path = kwargs.get("root_output_model_dir_path")
    local_data_dir_path =  kwargs["ti"].xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir")
    dag_timestamp =  kwargs["ti"].xcom_pull(key="dag_timestamp", task_ids="prepare_local_dir")
    train_output_data_path = os.path.join(local_data_dir_path, f"train_{data_filename}")
    test_output_data_path = os.path.join(local_data_dir_path, f"test_{data_filename}")
    
    print("Training.....")


    model_filename = f"model_{dag_timestamp}.pkl"
    output_model_path = os.path.join(root_output_model_dir_path, model_filename)
    print(f"Saving a model as a pickle file: output_model_path={output_model_path}")

with DAG(
    DAG_NAME,
    schedule_interval="@once",
    start_date=days_ago(2),
    default_args=DEFAULT_ARGS,
    tags=['model'],
) as dag:

    prepare_local_dir = PythonOperator(
        task_id="prepare_local_dir",
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=prepare_local_dir_func,
    )

    download_data = PythonOperator(
        task_id="download_data",
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=download_data_func,
    )

    preprocess_data = PythonOperator(
        task_id="preprocess_data",
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=preprocess_data_func,
    )

    visualize_data = PythonOperator(
        task_id="visualize_data",
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=visualize_data_func,
    )

    train_model = PythonOperator(
        task_id="train_model",
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=train_model_func,
    )

    # A path to be deleted is read from XCOM.
    rm_command = 'rm -rf {{ ti.xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir") }}'
    remove_local_data = BashOperator(
        task_id='remove_local_data',
        bash_command=rm_command,
        dag=dag,
    )

    prepare_local_dir >> download_data >> preprocess_data >> (visualize_data, train_model) >> remove_local_data