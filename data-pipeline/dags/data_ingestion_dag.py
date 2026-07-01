"""
Data ingestion pipeline DAG
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': False,
}

dag = DAG(
    'data_ingestion_pipeline',
    default_args=default_args,
    description='Ingests loan portfolio data from source systems',
    schedule_interval='0 1 * * *',  # Daily at 1 AM
    catchup=False,
)


def extract_portfolio_data():
    """Extract portfolio data from source"""
    logger.info("Extracting portfolio data...")
    # Implementation to be added


def load_to_warehouse():
    """Load data to data warehouse"""
    logger.info("Loading data to warehouse...")
    # Implementation to be added


def validate_data_quality():
    """Validate data quality"""
    logger.info("Validating data quality...")
    # Implementation to be added


# Tasks
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_portfolio_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_to_warehouse,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_quality',
    python_callable=validate_data_quality,
    dag=dag,
)

# Set dependencies
extract_task >> load_task >> validate_task
