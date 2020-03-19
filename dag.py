import json
import os

from datetime import timedelta

from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from main import prepare_email

# Declare default arguments and initialize DAG
args = {
    'owner': 'Weather Prophet',
    'start_date': days_ago(2)
}

dag = DAG(
    dag_id='weather_forecast',
    default_args=args,
    schedule_interval=timedelta(days=1)
)

# Load subscribers
with open(os.path.dirname(os.path.abspath(__file__)) + '/subscribers.json') as f:
    subscribers = json.load(f)

# Action at exit
exit_summary = BashOperator(
    task_id='exit_summary',
    bash_command="""
    echo "Weather forecasts sent to the following adresses:"
    {% for subscriber in subscribers %}
        echo "{{ subscriber.email }}"
    {% endfor %}
    """,
    params={'subscribers': subscribers},
    dag=dag
)

# Create tasks per subscribers
for i, subscriber in enumerate(subscribers):
    send_forecast = PythonOperator(
        task_id='send_forecast_' + str(i),
        python_callable=prepare_email,
        op_kwargs={'cities': subscriber['cities']},
        dag=dag
    )
    send_forecast >> exit_summary
