.PHONY: build down up logs exec restart

ENVS := AIRGLUE_GCP_PROJECT_ID=$(AIRGLUE_GCP_PROJECT_ID) \
	AIRGLUE_GCP_REGION=$(AIRGLUE_GCP_REGION) \
	AIRGLUE_GCP_INFRA_PROJECT_ID=$(AIRGLUE_GCP_INFRA_PROJECT_ID)

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