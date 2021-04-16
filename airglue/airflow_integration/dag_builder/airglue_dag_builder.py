# DAG - DO NOT REMOVE THIS LINE, IT IS REQUIRED BY AIRFLOW TO SCAN THIS FILE AND CREATE DAGS

import logging
import os
import sys

import pendulum

from typing import Dict, Any, List
from pydoc import locate

# Add DAG root path to PYTHONPATH
sys.path.append(os.environ['AIRGLUE_SRC_PATH'])

from airflow.models import Variable
from airglue.airflow_integration.dag_builder import dag_builder_util
from airglue.common.configuration import env_config
from airglue.common import configuration, schema
from airglue.common import parser


def init_config(config_path, config_extension='yaml') -> List[Dict[str, Any]]:
    details = []
    logging.debug('### Path to DAGs: {}'.format(config_path))
    directories = [d for d in os.listdir(config_path) if '.' not in d]
    logging.debug('### Scanning directories: {}'.format(directories))

    for dag_name in directories:
        dag_config_path = os.path.join(config_path, dag_name)
        config_file = os.path.join(dag_config_path, 'config.' + config_extension)
        logging.debug(f'### Unverified config file: {config_file}')
        if not os.path.exists(config_file):
            logging.debug('### Ignoring {}'.format(config_file))
            continue
        with open(config_file) as config_fp:
            details.append({
                'dag_name': dag_name,
                'dag_config_path': dag_config_path,
                'dag_config': parser.yaml_to_dict(y=config_fp.read())
            })

    return details


def dag_config_to_params(dag_config: schema.DagConfig):
    params = {'envs': {}, 'vars': {}}
    envs = dag_config.envs if dag_config.envs else []
    vars = dag_config.vars if dag_config.vars else []

    for env in envs:
        params['envs'][env] = os.environ.get(env)

    for var in vars:
        try:
            params['vars'][var] = Variable.get(var, deserialize_json=True, default_var=None)
        except ValueError:
            params['vars'][var] = Variable.get(var, default_var=None)

    for key, value in dag_config.params.items():
        if key in ['envs', 'vars']:
            continue

        params[key] = value

    return params


def create_operator(dag, dag_config_path, params: dict, task: schema.Task):
    operator_factory_class = locate(task.operator_factory)
    operator_class = locate(task.operator)

    if operator_factory_class is None:
        raise RuntimeError(f'{task.operator_factory} not found for DAG "{dag.dag_id}"')

    if operator_class is None:
        raise RuntimeError(f'{task.operator} not found for DAG "{dag.dag_id}"')

    return operator_factory_class.create(
        operator=operator_class,
        dag_config_path=dag_config_path,
        dag=dag,
        task_id=task.identifier,
        params=params,
        provide_context=True, **task.arguments
    )


def build(**kwargs):
    dags = []
    exceptions = []

    for details in init_config(config_path=kwargs['config_path']):
        logging.debug(f'### Dag Details: {details}')
        dag_name = details['dag_name']
        dag_config_path = details['dag_config_path']
        dag_config = details['dag_config']

        dag_id = f'{configuration.PROJECT_NAME}__{dag_name}'
        try:
            dag_config = schema.load_dag_schema(payload=dag_config)
        except schema.InvalidDagConfig as e:
            exceptions.append({'dag_id': dag_id, 'e': e})
            continue

        # DAG will be excluded if disabled
        if not dag_config.enabled:
            logging.info(f'DAG {dag_config_path} is disabled')
            continue

        # parse dag vars
        params = dag_config_to_params(dag_config=dag_config)

        dag = dag_builder_util.create_dag(
            dag_id=dag_id,
            start_date=dag_builder_util.get_default_dag_start_date(
                tzinfo=pendulum.timezone(dag_config.timezone)
            ),
            schedule_interval=dag_config.schedule_interval,
            template_searchpath=[dag_config_path],
        )

        dag.doc_md = dag_config.description

        globals()[dag_id] = dag
        dags.append({'dag_id': dag_id, 'dag': dag})

        created_operator_tasks = {}

        for task in dag_config.tasks:
            logging.debug(f'### task: {task.__dict__}')
            operator = create_operator(dag=dag, dag_config_path=dag_config_path, params=params, task=task)
            created_operator_tasks[task.identifier] = operator
            operator.doc_md = task.description

        for task in dag_config.tasks:
            if len(task.dependencies) == 0:
                continue
            for dependency in task.dependencies:
                if dependency not in created_operator_tasks:
                    raise RuntimeError('identifier `{}` does not exist'.format(dependency))

                created_operator_tasks[dependency] >> created_operator_tasks[task.identifier]

    return dags, exceptions


_, global_exceptions = build(config_path=env_config.config_path)

if global_exceptions:
    raise RuntimeError(
        '....'.join(
            [f'#### Error for DAG {exception["dag_id"]}: {exception["e"]} ####' for exception in global_exceptions])
    )
