from airglue.common import schema
from airglue.common.parser import yaml_to_dict


def test_schema_is_valid():
    valid_config = """
enabled: true
schedule_interval: "0 2 * * *"
timezone: "Europe/London"
tasks:
  - identifier: example_gcs_to_bq
    operator: airflow.contrib.operators.gcs_to_bq.GoogleCloudStorageToBigQueryOperator
    argument_factory: airglue.contrib.operator_arguments_factory.default.DefaultOperatorArgumentsFactory
    arguments:
      bucket: "{{ GCP_PROJECT_ID }}_airglue_example_bucket"
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
    assert first_task.argument_factory == 'airglue.contrib.operator_arguments_factory.default.DefaultOperatorArgumentsFactory'
    assert first_task.arguments == {
        'bucket': '{{ gcp_project_id }}_airglue_example_bucket',
        'source_objects': "bigquery/us-states/us-states.csv",
        'destination_project_dataset_table': "airglue_example.gcs_to_bq_table"
    }
