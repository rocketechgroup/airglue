# Tools to generate the value string for GCP secret manager

## airflow_connection_gcp
This script generates the Google Cloud Platform connection URI by putting the service account key into secret manager itself. 

To generate the Connection URI, run 
```bash
PROJECT_ID=<gcp project id of the airflow connection> GCP_JSON_KEY=<the service account json key with no line breaks> python3 airflow_connection_gcp.py
```

The output would look like 
```
google-cloud-platform://?extra__google_cloud_platform__project=<project_id>&extra__google_cloud_platform__keyfile_dict=<encoded json key>
```