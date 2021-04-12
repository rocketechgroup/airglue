from airflow.contrib.hooks.bigquery_hook import BigQueryHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class QueryToTable(BaseOperator):
    template_fields = ('sql', 'destination_dataset_table', 'labels')
    template_ext = ('.sql',)
    ui_color = '#e6f0e4'

    @apply_defaults
    def __init__(self,
                 sql,
                 destination_dataset_table,
                 write_disposition='WRITE_EMPTY',
                 create_disposition='CREATE_IF_NEEDED',
                 bigquery_conn_id='bigquery_default',
                 delegate_to=None,
                 labels=None,
                 encryption_configuration=None,
                 allow_large_results=False,
                 flatten_results=None,
                 udf_config=None,
                 use_legacy_sql=False,
                 maximum_billing_tier=None,
                 maximum_bytes_billed=None,
                 query_params=None,
                 schema_update_options=None,
                 priority='INTERACTIVE',
                 time_partitioning=None,
                 api_resource_configs=None,
                 cluster_fields=None,
                 location=None,
                 *args,
                 **kwargs):
        super(QueryToTable, self).__init__(*args, **kwargs)
        self.sql = sql
        self.destination_dataset_table = destination_dataset_table
        self.write_disposition = write_disposition
        self.create_disposition = create_disposition
        self.bigquery_conn_id = bigquery_conn_id
        self.delegate_to = delegate_to
        self.labels = labels
        self.encryption_configuration = encryption_configuration
        self.allow_large_results = allow_large_results
        self.flatten_results = flatten_results
        self.udf_config = udf_config
        self.use_legacy_sql = use_legacy_sql
        self.maximum_billing_tier = maximum_billing_tier
        self.maximum_bytes_billed = maximum_bytes_billed
        self.query_params = query_params
        self.schema_update_options = schema_update_options
        self.priority = priority
        self.time_partitioning = time_partitioning
        self.api_resource_configs = api_resource_configs
        self.cluster_fields = cluster_fields
        self.location = location

    def execute(self, context):
        self.log.info(
            f'Executing query """\n{self.sql}\n""" '
            f'and save to table: "{self.destination_dataset_table}"'
        )
        hook = BigQueryHook(bigquery_conn_id=self.bigquery_conn_id, delegate_to=self.delegate_to)
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.run_query(
            sql=self.sql,
            destination_dataset_table=self.destination_dataset_table,
            write_disposition=self.write_disposition,
            create_disposition=self.create_disposition,
            labels=self.labels,
            encryption_configuration=self.encryption_configuration,
            allow_large_results=self.allow_large_results,
            flatten_results=self.flatten_results,
            udf_config=self.udf_config,
            use_legacy_sql=self.use_legacy_sql,
            maximum_billing_tier=self.maximum_billing_tier,
            maximum_bytes_billed=self.maximum_bytes_billed,
            query_params=self.query_params,
            schema_update_options=self.schema_update_options,
            priority=self.priority,
            time_partitioning=self.time_partitioning,
            api_resource_configs=self.api_resource_configs,
            cluster_fields=self.cluster_fields,
            location=self.location
        )
