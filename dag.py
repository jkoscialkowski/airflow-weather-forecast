import json
import os

from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from main import prepare_forecast, send_forecast

# Declare default arguments and initialize DAG
args = {
    'owner': 'Weather Prophet',
    'start_date': days_ago(2)
}

dag = DAG(
    dag_id='weather_forecast',
    default_args=args,
    schedule_interval='@daily'
)

# Load subscribers
with open(os.path.dirname(os.path.abspath(__file__)) + '/subscribers.json') as f:
    subscribers = json.load(f)

# Action at exit
exit_summary = BashOperator(
    task_id='exit_summary',
    bash_command="""
    echo "Weather forecasts sent to the following adresses:"
    {% for subscriber in params.subscribers %}
        echo "{{ subscriber.email }}"
    {% endfor %}
    """,
    params={'subscribers': subscribers},
    dag=dag
)

# Create tasks per subscribers
for i, subscriber in enumerate(subscribers):
    pf = PythonOperator(
        task_id='prepare_forecast_' + str(i),
        python_callable=prepare_forecast,
        op_kwargs={'cities': subscriber['cities']},
        dag=dag
    )

    sf = PythonOperator(
        task_id='send_forecast_' + str(i),
        provide_context=True,
        python_callable=send_forecast,
        op_kwargs={
            'email': subscriber['email'],
            'cities': subscriber['cities'],
            'prev_task_id': 'prepare_forecast_' + str(i)
        },
        dag=dag
    )

    pf >> sf >> exit_summary
