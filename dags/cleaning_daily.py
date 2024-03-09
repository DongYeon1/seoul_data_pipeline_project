from plugins.cleaning import Cleaning
from airflow import DAG
from datetime import timedelta,datetime
from airflow.decorators import task
from plugins import filter
from plugins.utils import FileManager
from plugins.s3 import S3Helper
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

@task
def road_cleaning(**context):
    try:
        execution_date = context['execution_date'].date()
        data = Cleaning.read_csv_to_df('road', execution_date, filter.column_indexes['road'])
        checked_data = Cleaning.check_pk_validation(Cleaning.rename_cols(data, 'road'), 'division_name')
        unified_data = Cleaning.unify_null(checked_data)

        result_data = Cleaning.filter(unified_data, 'road')

        save_path = 'temp/seoul_road/cleaning/'
        file_name = f'{execution_date}.parquet'
        path = save_path+file_name

        FileManager.mkdir(save_path)

        result_data.to_parquet(path, index=False)

        s3_key = 'cleaned_data/seoul_road/' + file_name

        S3Helper.upload(aws_conn_id, bucket_name, s3_key, path, True)

        FileManager.remove(path)

    
    except:
        pass

@task
def air_cleaning(**context):
    try:
        execution_date = context['execution_date'].date()
        data = Cleaning.read_csv_to_df('air', execution_date, filter.column_indexes['air'])
        checked_data = Cleaning.check_pk_validation(Cleaning.rename_cols(data, 'air'), 'gu')

        unified_data = Cleaning.unify_null(checked_data)
        result_data = Cleaning.filter(unified_data, 'air')

        save_path = 'temp/seoul_air/cleaning/'
        file_name = f'{execution_date}.parquet'
        path = save_path+file_name

        FileManager.mkdir(save_path)

        result_data.to_parquet(path, index=False)

        s3_key = 'cleaned_data/seoul_air/' + file_name

        S3Helper.upload(aws_conn_id, bucket_name, s3_key, path, True)

        FileManager.remove(path)

    except:
        pass

@task
def housing_cleaning(**context):
        try:
            execution_date = context['execution_date'].date()
            data = Cleaning.read_csv_to_df('housing', execution_date, filter.column_indexes['housing'])
            checked_data = Cleaning.check_pk_validation(Cleaning.rename_cols(data, 'housing'), 'gu')
            unified_data = Cleaning.unify_null(checked_data)

            result_data = Cleaning.filter(unified_data, 'housing')

            save_path = 'temp/seoul_air/housing/'
            file_name = f'{execution_date}.parquet'
            path = save_path+file_name

            FileManager.mkdir(save_path)

            result_data.to_parquet(path, index=False)

            s3_key = 'cleaned_data/seoul_housing/' + file_name

            S3Helper.upload(aws_conn_id, bucket_name, s3_key, path, True)

            FileManager.remove(path)
    
        except:
            pass

@task
def pop_cleaning(**context):
    try:
        execution_date = context['execution_date'].date() - timedelta(days=4)
        data = Cleaning.read_csv_to_df('pop', execution_date, filter.column_indexes['pop'])
        checked_data = Cleaning.check_pk_validation(Cleaning.rename_cols(data, 'pop'), 'gu')
        unified_data = Cleaning.unify_null(checked_data)

        result_data = Cleaning.filter(unified_data, 'pop')

        save_path = 'temp/seoul_pop/cleaning/'
        file_name = f'{execution_date}.parquet'
        path = save_path+file_name

        FileManager.mkdir(save_path)

        result_data.to_parquet(path, index=False)

        s3_key = 'cleaned_data/seoul_pop/' + file_name

        S3Helper.upload(aws_conn_id, bucket_name, s3_key, path, True)

        FileManager.remove(path)

    except:
        pass

with DAG(
    dag_id = 'cleaning_daily',
    start_date = datetime(2024,1,1),
    max_active_runs = 1,
    catchup = True,
    default_args = {
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    }
) as dag:
    aws_conn_id='aws_conn_id'
    bucket_name = 'de-team5-s3-01'
    
    trigger_dag_task = TriggerDagRunOperator(
        task_id='trigger_dag_task',
        trigger_dag_id='',
        execution_date='{{data_interval_start}}',
        reset_dag_run=True,
        poke_interval=60,
        allowed_states=['success', 'failed', 'upstream_failed']
    )

    [road_cleaning(),air_cleaning(),pop_cleaning(),housing_cleaning()] >> trigger_dag_task