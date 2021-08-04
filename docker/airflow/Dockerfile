ARG AIRFLOW_IMAGE_NAME="apache/airflow:2.1.2-python3.9"
FROM ${AIRFLOW_IMAGE_NAME}

# Install additional Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    pandas==1.3.0 \
    numpy==1.20.3 \
    scipy==1.7.0 \
    scikit-learn==0.24.2

CMD []