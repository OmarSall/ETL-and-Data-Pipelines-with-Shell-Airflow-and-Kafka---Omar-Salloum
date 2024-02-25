from datetime import timedelta
#DAG object, that we need to instantiate a DAG
from airflow import DAG
#Operators; we need this to write tasks
from airflow.operators.bash_operator import BashOperator
#This makes scheduling easy
from airflow.utils.dates import days_ago

#defining DAG arguments

#You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'Omar Salloum',
    'start_date': days_ago(0),
    'email': ['omar@salloum.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


#DAG definition
dag = DAG(
    dag_id='ETL_toll_data',
    default_args=default_args,
    description='Apache Airflow Final Assignment',
    schedule_interval=timedelta(days=1),
)

#first task - unzip data

unzip_data = BashOperator(
    task_id="unzip_data",
    bash_command="/home/project/airflow/dags/unzip_data.sh ",
    dag=dag,
)

"""
unzip_data.sh

!#/bin/bash

sudo mkdir -p /home/project/airflow/dags/finalassignment/staging

sudo chown -R 100999 /home/project/airflow/dags/finalassignment
sudo chmod -R g+rw /home/project/airflow/dags/finalassignment  
sudo chown -R 100999 /home/project/airflow/dags/finalassignment/staging
sudo chmod -R g+rw /home/project/airflow/dags/finalassignment/staging

sudo wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Final%20Assignment/tolldata.tgz

tar zxvf tolldata.tgz

"""

#second task - extract_data_from_csv

extract_data_from_csv = BashOperator(
    task_id="extract_data_from_csv",
    bash_command="/home/project/airflow/dags/extract_data_from_csv.sh ",
    dag=dag,
)

"""
extract_data_from_csv.sh

!#/bin/bash

echo "Extracting data from csv file - I Hope I will get a job after that xd"

cut -d "," -f1-4 /home/project/airflow/dags/finalassignment/staging/vehicle-data.csv > csv_data.csv

"""


#third task - extract_data_from_tsv file

extract_data_from_tsv = BashOperator(
    task_id="extract_data_from_tsv",
    bash_command="/home/project/airflow/dags/extract_data_from_tsv.sh ",
    dag=dag,
)

"""
extract_data_from_tsv.sh

!#/bin/bash

echo "Extracting data from tsv file"

tr "\t" "," < /home/project/airflow/dags/finalassignment/staging/tollplaza-data.tsv > /home/project/airflow/dags/finalassignment/staging/tsv_data_not_ready.csv

cut -d "," -f5-7 /home/project/airflow/dags/finalassignment/staging/tsv_data_not_ready.csv > /home/project/airflow/dags/finalassignment/staging/tsv_data.csv


"""

#fourth task - extract_data_from_fixed_width file

extract_data_from_fixed_width = BashOperator(
    task_id="extract_data_from_fixed_width",
    bash_command="/home/project/airflow/dags/extract_data_from_fixed_width.sh ",
    dag=dag,
)

"""
extract_data_from_fixed_width.sh

!#/bin/bash

gawk '$1=$1' FIELDWIDTHS='6 25 8 9 10 4 6' OFS=, /home/project/airflow/dags/finalassignment/staging/payment-data.txt > /home/project/airflow/dags/finalassignment/staging/payment.csv

cut -d ","  -f6,7 /home/project/airflow/dags/finalassignment/staging/payment.csv > /home/project/airflow/dags/finalassignment/staging/fixed_width_data.csv
"""


#fifth task - consolidate_data

consolidate_data = BashOperator(
    task_id="consolidate_data",
    bash_command="/home/project/airflow/dags/consolidate_data.sh ",
    dag=dag,
)

"""
consolidate_data.sh

!#/bin/bash

paste -d "," csv_data.csv tsv_data.csv fixed_width_data.csv > /home/project/airflow/dags/finalassignment/staging/extracted_data.csv

"""

#sixth task - transform_data

transform_data = BashOperator(
    task_id="transform_data",
    bash_command="/home/project/airflow/dags/transform_data.sh ",
    dag=dag,
)

"""
transform_data.sh

!#/bin/bash

sed 's/[^,]*/\U&/2' /home/project/airflow/dags/finalassignment/staging/extracted_data.csv > /home/project/airflow/dags/finalassignment/staging/transformed_data.csv

"""


"""
paste cut -d "," -f1-3 extracted_data.csv  (cut -d "," -f4 | tr [:lower:] [:upper:]) < extracted_data.csv  > transformed_data.csv


"""


unzip_data >> extract_data_from_csv >> extract_data_from_tsv >> extract_data_from_fixed_width >> consolidate_data >> transform_data
