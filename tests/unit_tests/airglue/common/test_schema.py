from airglue.common import schema
from airglue.common.parser import yaml_to_dict


def test_schema_is_valid_without_vars():
    valid_config = """
enabled: true
schedule_interval: "0 2 * * *"
timezone: "Europe/London"
tasks:
  - identifier: example_gcs_to_bq
    operator: airflow.contrib.operators.gcs_to_bq.GoogleCloudStorageToBigQueryOperator
    operator_factory: airglue.contrib.operator_factory.default.DefaultOperatorFactory
    arguments:
      bucket: "airglue_example_bucket"
      source_objects: "bigquery/us-states/us-states.csv"
      destination_project_dataset_table: "airglue_example.gcs_to_bq_table"
    """
    config_dict = yaml_to_dict(valid_config)
    dag_config = schema.load_dag_schema(config_dict)

    assert dag_config.enabled
    assert dag_config.schedule_interval == '0 2 * * *'
    assert dag_config.timezone == 'Europe/London'
    assert len(dag_config.tasks) == 1

    first_task = dag_config.tasks.pop()
    assert first_task.identifier == 'example_gcs_to_bq'
    assert first_task.operator == 'airflow.contrib.operators.gcs_to_bq.GoogleCloudStorageToBigQueryOperator'
    assert first_task.operator_factory == 'airglue.contrib.operator_factory.default.DefaultOperatorFactory'
    assert first_task.arguments == {
        'bucket': 'airglue_example_bucket',
        'source_objects': "bigquery/us-states/us-states.csv",
        'destination_project_dataset_table': "airglue_example.gcs_to_bq_table"
    }


def test_schema_is_valid_with_vars():
    valid_config = """
enabled: true
schedule_interval: "0 2 * * *"
timezone: "Europe/London"
params:
  default_dataset: airglue_example
  envs: 
    - AIRGLUE_GCP_PROJECT_ID
    - AIRGLUE_GCP_REGION
  vars:
    - example_bucket_name
tasks:
  - identifier: x
    operator: x
    operator_factory: x
    """
    config_dict = yaml_to_dict(valid_config)
    dag_config = schema.load_dag_schema(config_dict)

    assert dag_config.enabled
    assert dag_config.schedule_interval == '0 2 * * *'
    assert dag_config.timezone == 'Europe/London'
    assert dag_config.params['envs'] == ['AIRGLUE_GCP_PROJECT_ID', 'AIRGLUE_GCP_REGION']
    assert dag_config.params['vars'] == ['example_bucket_name']
    assert dag_config.params['default_dataset'] == 'airglue_example'
    assert len(dag_config.tasks) == 1
