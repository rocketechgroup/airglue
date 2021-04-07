.PHONY: build down up logs exec restart

AIRGLUE_GCP_PROJECT_ID=# REPLACE ME
AIRGLUE_COMPOSER_AIRFLOW_VERSION=1.10.14

ENVS := AIRGLUE_GCP_PROJECT_ID=$(AIRGLUE_GCP_PROJECT_ID) \
	AIRGLUE_COMPOSER_AIRFLOW_VERSION=$(AIRGLUE_COMPOSER_AIRFLOW_VERSION)

build:
	$(ENVS) docker-compose -f docker-compose.yml up -d --build webserver

down:
	$(ENVS) docker-compose -f docker-compose.yml down

up:
	$(ENVS) docker-compose -f docker-compose.yml up -d

restart:
	make down && make up

logs:
	docker logs airglue_webserver -f

exec:
	docker exec -it airglue_webserver /bin/bash -c "source ./script/exec_entrypoint.sh; /bin/bash"