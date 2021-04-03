# Airglue
Writing python code to create Airflow DAGs and link Airflow Operators is very repetitive and not accessible to users don't have a programming background. 

Airglue uses a simple YAML config file to create DAGs and glue Airflow Operators together with no programming required.

## Design Concept
TBC

## Getting Started
The following instructions will get Airglue up and running in Docker.

### Start up
```
make up AIRGLUE_GCP_PROJECT_ID={YOUR GCP SANDBOX PROJECT ID}
```

Go to `localhost:8082`

You should how see the example DAG and to get started, see the [example dag here](airglue/example/example_glue).

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

## Credits
This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: DOP https://github.com/teamdatatonic/dop   
Copyright (c) 2021 Datatonic   
License MIT https://github.com/teamdatatonic/dop/blob/master/LICENSE.md   