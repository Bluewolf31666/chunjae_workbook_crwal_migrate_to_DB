import datetime
from email_html import html
from email_html_fail import fail_html
from airflow import DAG
from airflow.operators.email import EmailOperator
class alert:
    def __init__(self):
        pass 

    def success(self):
        email = EmailOperator(
            task_id = 'send by success',
            to = 'chh6632@chunjae.co.kr',
            subject = f'Airflow 성공 메일입니다 완료시간 : {datetime.datetime.now()}',
            html_content = html
        ) 

    def fail(self):
        email = EmailOperator(
            task_id = 'send by fail',
            to = 'chh6632@chunjae.co.kr',
            subject = f'Airflow 실패 메일입니다. 실패시간 : {datetime.datetime.now()}',
            html_content = fail_html
            )
    
