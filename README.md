# Airglue
Create Airflow DAGs and orchestrate dependencies between Operators can be somewhat repetitive and not easy for users without a programming background. 
Airglue's configuration driven approach makes this easy to manage without needing to write any Python at all.

## TOC
* [Design Concept](#design-concept)
* [Key Features](#key-features)
* [Getting Started](#getting-started)
   * [Prerequisites](#prerequisites)
   * [Build and Start up](#build-and-start-up)
   * [Start up without building](#start-up-without-building)
   * [Shut down](#shut-down)
   * [Restart](#restart)
   * [Inspect Container Logs](#inspect-container-logs)
   * [SSH into the container](#ssh-into-the-container)
   * [Example DAG](#example-dag)
   * [DAG Configuration Explained](#dag-configuration-explained)
      * [The following structure is used to define a DAG](#the-following-structure-is-used-to-define-a-dag)
      * [The following structure is used to define a task within a DAG](#the-following-structure-is-used-to-define-a-task-within-a-dag)
   * [Custom Operator](#custom-operator)
   * [Operator Factory](#operator-factory)
   * [The Secret Manager Backend](#the-secret-manager-backend)
   * [Airflow / Cloud Composer Versions](#airflow--cloud-composer-versions)
* [TODO](#todo)
* [Additional Examples](#additional-examples)
   * [Example Dataflow Runner](#example-dataflow-runner)
* [Credits](#credits)

## Design Concept
By defining a YAML config such as the one in [this example](airglue/example/example_glue/config.yaml), you would be able to dynamically create a complex DAG flow like this   
![Example DAG view](docs/example_dag_graph_view.png)

With powerful templating & rendering   
![Example DAG templating](docs/example_dag_templating_and_rendering.png)

And producing output to these tables in BigQuery   
![Example DAG output](docs/example_dag_bq_output.png)

For more details on exactly how this works, see [Example DAG](#example-dag) and [DAG Configuration Explained](#dag-configuration-explained)

## Key Features
- User can create DAGs and manage Operator dependencies through a simple YAML file
- Plugin based architecture allows components such as custom Operators and Operator Factory classes to be added which helps eliminate most duplication
- Environment, Airflow and static variables can all be defined in the YAML and made available through `{{ params }}` ready to be used in the Airflow templating context

## Getting Started
The following instructions will get Airglue up and running in Docker on your laptop (Mac or Linux). 
The whole process should only take around 10-15 minutes depending on your internet connection speed. 

### Prerequisites
1) Have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
1) Have the [gcloud sdk](https://cloud.google.com/sdk/docs/install) installed
1) Have a GCP [default application credential](https://cloud.google.com/sdk/gcloud/reference/auth/application-default) generated under `~/.config/gcloud/application_default_credentials.json`.
1) Create a service account on your GCP sandbox project and call it `airglue@<project_id>.iam.gserviceaccount.com`, generate a JSON key and save to Secret Manager as a new secret with a name `airflow-connections-gcp_airglue`. See [The Secret Manager Backend](#the-secret-manager-backend) for more details on how to generate the secret value. 
> The reason service account impersonation is not used is due to there is no support on Airflow V1 to the built-in operators.
> It is important to rotate the key regularly when using service account keys. 
> Airflow V2 made this available via the `impersonation_chain` argument. 
> See https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/operators/bigquery/index.html 

### Build and Start up
```
make build
```

Go to `localhost:8082`

You should how see the example DAG and to get started, see the [example dag here](airglue/example/example_glue).

### Start up without building
It is quicker to start up Airglue without re-building each time
```
make up
```

### Shut down
```
make down
```

### Restart
```
make restart
```

### Inspect Container Logs
```
make logs
```

### SSH into the container
```
make exec
```

### Example DAG
There is an example DAG created in this repository called [example_glue](airglue/example/example_glue). It is designed to be a `show case` DAG that demos a lot of supported features in Airglue. 

In order for this DAG to work, the `airglue@<project_id>.iam.gserviceaccount.com` service account must be granted the following roles
- Project Level: BigQuery Data Editor and BigQuery Job User
- Bucket Level: Storage Object Admin on the bucket defined below using the environment variable `AIRGLUE_EXAMPLE_BUCKET_NAME`

And the `make` command must be executed with the following variables
- `AIRGLUE_SANDBOX_PROJECT_ID`: A GCP project id for your sandbox environment.
- `AIRGLUE_EXAMPLE_BUCKET_NAME`: An example GCS bucket used to persist data. The service account must be able to write into this bucket.

And to run the example DAG use something like
```
make build AIRGLUE_SANDBOX_PROJECT_ID={replace me} AIRGLUE_EXAMPLE_BUCKET_NAME={replace me}
```
### DAG Configuration Explained
#### The following structure is used to define a DAG
```yaml
enabled: { optional<true|false>. Enable or disable the DAG, default is true if not specified. Disabled DAGs won't show up in the Airflow GUI }
schedule_interval: { required<cron expression>. A valid CRON expression used to setup DAG schedule, if no schedule is required, set to `null`. i.e. "0 2 * * *" or null. You may use https://crontab.guru/ to validate your CRON expression }
timezone: { required<timezone>. Timezone for the schedule. I.e. "Europe/London". Local time is always preferred so that processing can be done exactly at the right time for the correct data boundaries }
description: { optional<string with markdown support>. A description for the DAG }
params: { optional<key:value>. Static key value pairs to be loaded and made available as {{ params }} in any context in Airflow with Jinja templating enabled }
# i.e. 
# default_dataset: airglue_example can be referenced by {{ params.default_dataset }}

envs: { optional<list>. A list of environment variables to be loaded and made available as {{ params.envs.<name> }}, undefined ones will be omitted }
# i.e. the following can be referenced by {{ params.envs.AIRGLUE_SANDBOX_PROJECT_ID }}
# - AIRGLUE_SANDBOX_PROJECT_ID

vars: { optional<list>. It is possible to access airflow variables by using {{ var.value.get('my.var', 'fallback') }}, but you can also make them available under {{ params.vars.<name> }} to be more explicit for the DAG by defining them here, undefined ones will be omitted }
# i.e. the following can be referenced by {{ params.vars.example_bucket_name }}
# - example_bucket_name
```
To to the [Example DAG](airglue/example/example_glue) to see a working version of this.

#### The following structure is used to define a task within a DAG
```yaml
- identifier: { required<string>. Identifier for the task, must be unique within a DAG }
  operator: { required<string>. Fully qualified airflow operator name, i.e. airflow.contrib.operators.gcs_to_bq.GoogleCloudStorageToBigQueryOperator }
  operator_factory: { optional<string>. Fully qualified operator factory name, i.e. airglue.contrib.operator_factory.default.DefaultOperatorFactory, but if `DefaultOperatorFactory` is all that is required, this arguments can be omitted }
  arguments: { optional<key:value>. Key value pairs translated into Airflow Operator arguments. }
  # i.e. source_format: "NEWLINE_DELIMITED_JSON" 
  description: { optional<string with markdown support>. A description for the task }
  dependencies: { optional<list>. A list of task identifiers this task depends on, used to create the link between Airflow Operators within a DAG }
  # i.e. 
  # - task_identifier_1
  # - task_identifier_2
```
To to the [Example DAG](airglue/example/example_glue) to see a working version of this.

### Custom Operator
Under [airglue/contrib/operator](airglue/contrib/operator), custom Airflow Operators can be defined if Airflow does not have one to fulfill the requirements or you simply prefer to write your own so that there is no limit to what Airglue can execute.

See  [airglue/contrib/operator/bigquery/query_runner.py](airglue/contrib/operator/bigquery/query_runner.py) as an example.

### Operator Factory
Operator Factory is a concept introduced to make the configuration file more compact and easier to read, it can also be used to define common abstractions so that the configuration file becomes smaller hence much quicker to add new integrations.

Operator Factories can be added to [airglue/contrib/operator_factory](airglue/contrib/operator_factory) and by default the [default](airglue/contrib/operator_factory/default.py) Operator Factory is used.

### The Secret Manager Backend
> Important: requires Airflow version >=1.10.10   
> Important: your user group must have been given the `Secret Manager Secret Accessor` role in order to access the secret   

There are situations when using a secret (i.e. in Airflow Connections or Variables) is not avoidable. Airglue uses [Secret Manager](https://cloud.google.com/secret-manager) as the secret backend so that you do not have to store any credentials (such as service account keys) inside Airflow / Cloud Composer. 
This makes storing secret more secure and easy to manage. For example, you can setup key rotation automation and it only has to be done in one place which is secret manager. 

The Secret Manager Backend can be enabled by supplying the following Airflow environment variables
```
AIRFLOW__SECRETS__BACKEND: "airflow.providers.google.cloud.secrets.secret_manager.CloudSecretManagerBackend"
AIRFLOW__SECRETS__BACKEND_KWARGS: '{"project_id": "${AIRGLUE_SANDBOX_PROJECT_ID}", ...}'
```

On the Local Docker Composer environment, this has been done in [docker-composer.yaml](docker-compose.yml). 
Because secrets stored in Secret Manager has to be a valid URI. I.e. for a Airflow GCP connection, the secret value has to be in the format of
```
google-cloud-platform://?extra__google_cloud_platform__project={project_id}&extra__google_cloud_platform__keyfile_dict={quoted_key}"
```
To make this easier to generate, we've created a collection of tools under [tools/secret_value_creator](tools/secret_value_creator) which can be used to generate the URI.

For more information on exactly how to use this, see [Alternative secrets backend](https://airflow.apache.org/docs/apache-airflow/1.10.10/howto/use-alternative-secrets-backend.html)

### Airflow / Cloud Composer Versions
In order to make the setup compatible with [Cloud Composer](https://cloud.google.com/composer) as much as possible, we've created a separate release for each Composer version under [Local Docker Release](infrastructure/docker/release). 
There is a default one specified in the `Makefile` which is the latest supported version by Cloud Composer, but it can be overwritten by passing in `AIRGLUE_COMPOSER_AIRFLOW_VERSION` when running any `make` command. 
I.e. 
```
make build AIRGLUE_COMPOSER_AIRFLOW_VERSION=1.10.10
```

We aim to align the Airflow support to the latest 3 versions on Cloud Composer. Any older versions will still be available in the repository but will no longer be supported.
See [Composer versions](https://cloud.google.com/composer/docs/concepts/versioning/composer-versions) to check what are the latest versions.  

## TODO
- Windows user support

## Additional Examples
### Example Dataflow Runner
This example shows how to run a Batch Java Dataflow job using a dedicated DataFlow controller service account.    
To use the [Example Dataflow Runner](airglue/example/example_dataflow_runner), 

1. Create the `dataflow-controller` service account and assign the following roles, see more about controller service account [here](https://cloud.google.com/dataflow/docs/concepts/security-and-permissions#controller_service_account)
    - Project level: Dataflow Admin
    - Project level: Dataflow Worker
    - Bucket Level: Storage Object Admin
1. Grant the `airglue` service account the following roles
    - Project level: Dataflow Admin
    - Service Account Level: Allow the `airglue` service account to `act as `dataflow-controller` by granting it the `Service Account User` role. 
1. Upload the bundled jar to `gs://{{ params.vars.AIRGLUE_EXAMPLE_BUCKET_NAME }}/jars/`

## Credits
This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: DOP https://github.com/teamdatatonic/dop   
Copyright (c) 2021 Datatonic   
License MIT https://github.com/teamdatatonic/dop/blob/master/LICENSE.md   