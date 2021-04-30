import os
from urllib import parse

project_id = os.environ['PROJECT_ID']
gcp_json_key = os.environ['GCP_JSON_KEY']
quoted_key = parse.quote_plus(gcp_json_key)

print(
    f"google-cloud-platform://?extra__google_cloud_platform__project={project_id}&extra__google_cloud_platform__keyfile_dict={quoted_key}"
)
