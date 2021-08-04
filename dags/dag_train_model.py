from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

DAG_NAME = "train_model"
DEFAULT_ARGS = {
    "data_url": "",
    "root_local_data_dir_path": "/data",
    "root_output_model_dir_path": "",
}

def prepare_local_dir_func(**kwargs):
    root_local_data_dir_path = kwargs.get("root_local_data_dir_path")

    dir_name = "{}_{}".format(kwargs["dag"].dag_id , datetime.now().strftime("%Y%m%d_%H%M%S"))
    local_data_dir_path = os.path.join(root_local_data_dir_path, dir_name)
    print(f"Prepare a data directory: local_data_dir_path={local_data_dir_path}")

    if not os.path.exists(local_data_dir_path):
        os.makedirs(local_data_dir_path)

    # Share a generated path with other tasks
    kwargs["ti"].xcom_push(key="local_data_dir_path", value=local_data_dir_path)

def download_data_func(**kwargs):
    local_data_dir_path =  kwargs["ti"].xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir")
    print(f"Use a data directory: local_data_dir_path={local_data_dir_path}")
    pass

with DAG(
    DAG_NAME,
    schedule_interval="@once",
    start_date=days_ago(2),
    default_args=DEFAULT_ARGS,
    tags=['model'],
) as dag:

    prepare_local_dir = PythonOperator(
        task_id='prepare_local_dir',
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=prepare_local_dir_func,
    )

    download_data = PythonOperator(
        task_id='download_data',
        provide_context=True,
        op_kwargs=DEFAULT_ARGS,
        python_callable=download_data_func,
    )

    # A path to be deleted is read from XCOM.
    rm_command = 'rm -rf {{ ti.xcom_pull(key="local_data_dir_path", task_ids="prepare_local_dir") }}'
    remove_local_data = BashOperator(
        task_id='remove_local_data',
        bash_command=rm_command,
        dag=dag,
    )

    prepare_local_dir >> download_data >> remove_local_data