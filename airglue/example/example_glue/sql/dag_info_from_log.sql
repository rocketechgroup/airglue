SELECT dag_id, task_id, event, DATE(TIMESTAMP_SECONDS(CAST(execution_date AS INT64))) as source_timestamp, owner, TIMESTAMP_SECONDS(CAST(dttm AS INT64)) as log_timestamp, CURRENT_TIMESTAMP() as insertion_timestamp
FROM `{{ params.default_dataset }}.postgres_to_gcs_airflow_db_log`
WHERE DATE(TIMESTAMP_SECONDS(CAST(execution_date AS INT64))) = '{{ ds }}';