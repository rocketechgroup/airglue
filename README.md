# Airglue
Creating Airflow DAGs and orchestrate dependencies between Operators can be somewhat repetitive and not easy for users without a programming background. 
Airglue's configuration driven approach makes this easy to manage without needing to write any Python at all.

## TOC
* [Design Concept](#design-concept)
* [Getting Started](#getting-started)
   * [Start up](#start-up)
   * [Shut down](#shut-down)
   * [Restart](#restart)
   * [Inspect Container Logs](#inspect-container-logs)
   * [SSH into the container](#ssh-into-the-container)
* [Credits](#credits)

## Design Concept
TBC

## Getting Started
The following instructions will get Airglue up and running in Docker.

### Prerequisites
Create a service account with appropriate roles and save the key to `~/.config/gcloud/airglue/airglue-sandbox-sa.json` on your local machine. 

> The reason service account impersonation is not used is due to there is no support on Airflow V1 to the built-in operators.
> It is important to rotate the key regularly when using service account keys. 
> Airflow V2 made this available via the `impersonation_chain` argument. 
> See https://airflow.apache.org/docs/apache-airflow-providers-google/stable/_api/airflow/providers/google/cloud/operators/bigquery/index.html 

### Build and Start up
```
make build AIRGLUE_GCP_PROJECT_ID={YOUR GCP SANDBOX PROJECT ID}
```

Go to `localhost:8082`

You should how see the example DAG and to get started, see the [example dag here](airglue/example/example_glue).

### Start up without building
It is quicker to start up Airglue without re-building each time
```
make up AIRGLUE_GCP_PROJECT_ID={YOUR GCP SANDBOX PROJECT ID}
```

### Shut down
```
make down
```

### Restart
```
make restart AIRGLUE_GCP_PROJECT_ID={YOUR GCP SANDBOX PROJECT ID}
```

### Inspect Container Logs
```
make logs
```

### SSH into the container
```
make exec
```

## Features
TBC

## TODO
- Allow custom Airflow operators don't exist in Airflow to be created and used
- Add more Operator Factories to support common use cases (i.e. Ingestion from SQL databases with common query templates, etc)
- Make it support multiple composer versions
- Windows user support

## Credits
This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: DOP https://github.com/teamdatatonic/dop   
Copyright (c) 2021 Datatonic   
License MIT https://github.com/teamdatatonic/dop/blob/master/LICENSE.md   