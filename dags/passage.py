from datetime import datetime
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email import EmailOperator
from email_html import html
from email_html_fail import fail_html
from airflow.operators.python_operator import BranchPythonOperator

## 성공 실패 정의



# DAG 정의
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 9,4) ,
    'depends_on_past': False,
    'retries': 1,
    'email':['11'],
    'on_success_callback' :False,
    'on_failure_callback' :False,
}

dag = DAG(
    'passage',
    default_args=default_args,
    schedule_interval='0 17 * * *',  # 수동으로 실행하려면 None으로 설정합니다.
    catchup=False,
)

# 쿼리 및 저장 실행 (변수간 이동 되는 지 테스트)
select_cmd= "python3 /opt/airflow/dags/select_passage_id_update/main.py"
crawl_cmd= "python3 /opt/airflow/dags/pargraph_dev_update/main.py"

# 쿼리를 실행
quary_to_local = BashOperator(
    task_id='db_query',
    bash_command=select_cmd,
    dag=dag
)


# 결과를 로컬 파일 시스템에 저장
save_to_local = BashOperator(
        task_id='save_to_local',
    bash_command=crawl_cmd,
    dag=dag
)

send_to_success= EmailOperator(
    task_id='send_to_success',
    to = ['chh6632@chunjae.co.kr','cng3022@chunjae.co.kr'],
    subject = "지문 airflow 성공 메일입니다",
    html_content=html,
    trigger_rule='all_success',
    dag=dag
    )

send_to_fail= EmailOperator(
    task_id = 'send_to_fail',
    to = ['chh6632@chunjae.co.kr','cng3022@chunjae.co.kr'],
    subject = '지문 Airflow 실패 메일입니다.',
    html_content = fail_html,
    trigger_rule='one_failed',
    dag=dag
) 

def path():
    stat = True
    if stat:
        path='send_to_success'
    else:
        path='send_to_fail'
    return path

branch= BranchPythonOperator(
    task_id='branch',
    python_callable=path,
    dag=dag
)








# 태스크 간 의존성 설정
quary_to_local >> save_to_local >>branch>>[send_to_success,send_to_fail ]

