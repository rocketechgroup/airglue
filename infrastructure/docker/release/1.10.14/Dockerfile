FROM apache/airflow:1.10.14-python3.6
LABEL maintainer="Rocketech"

ARG AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

USER root

RUN apt-get update && apt-get install dos2unix wget -y && apt-get install software-properties-common -y

# Install java 8
RUN wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | sudo apt-key add -
RUN add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/
RUN apt-get update && apt-get install adoptopenjdk-8-hotspot -y

USER airflow

# Install composer dependencies & additional required dependencies not included in Composer
COPY requirements.composer.txt /pre-installed-requirements.txt
RUN set -ex \
    && pip install --user -r /pre-installed-requirements.txt

COPY --chown=airflow:airflow script/entrypoint.sh ${AIRFLOW_HOME}/script/entrypoint.sh
COPY --chown=airflow:airflow script/exec_entrypoint.sh ${AIRFLOW_HOME}/script/exec_entrypoint.sh

# Resolve windows line ending issues
RUN dos2unix -n ${AIRFLOW_HOME}/script/entrypoint.sh ${AIRFLOW_HOME}/script/entrypoint.sh
RUN dos2unix -n ${AIRFLOW_HOME}/script/exec_entrypoint.sh ${AIRFLOW_HOME}/script/exec_entrypoint.sh

# allow execution of entrypoint script
RUN chmod +x ${AIRFLOW_HOME}/script/entrypoint.sh