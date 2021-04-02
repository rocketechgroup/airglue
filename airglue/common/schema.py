import typing
import copy

from croniter import croniter
from typing import List, Dict, AnyStr

from marshmallow import validate, post_load, Schema, fields


class InvalidDagConfig(ValueError):
    pass


class IsValidCron(validate.Validator):
    default_message = 'Not a valid Cron Expression'

    def __call__(self, value) -> typing.Any:
        message = f'The schedule_interval expression `{value}` must be a valid CRON expression: ' \
                  'validate it here https://crontab.guru/'
        if not croniter.is_valid(value):
            raise validate.ValidationError(message)

        return value


class Task:
    def __init__(
            self,
            identifier: str,
            operator,
            operator_factory: str,
            arguments: Dict,
            dependencies: List[str]

    ):
        """
        @param identifier: Task Identifier
        @param operator: str representation of any class derived from airflow.models.baseoperator.BaseOperator
        @param operator_factory: str representation of any class derived from airglue.contrib.operator_factory.default.OperatorFactory
        @param arguments: a dict of arguments used by the argument factory class
        @param dependencies: an optional list of dependencies for this task
        """
        self.identifier = identifier
        self.operator = operator
        self.operator_factory = operator_factory
        self.arguments = arguments
        self.dependencies = dependencies


class TaskSchema(Schema):
    identifier = fields.Str(required=True)
    operator = fields.Str(
        required=True
    )
    operator_factory = fields.Str(
        required=False,
        missing='airglue.contrib.operator_factory.default.DefaultOperatorFactory'
    )
    arguments = fields.Dict(
        required=False,
        missing={}
    )
    dependencies = fields.List(
        cls_or_instance=fields.Str(),
        required=False,
        missing=[]
    )


class DagConfig:
    def __init__(self, enabled: bool, timezone: str, schedule_interval: str, tasks: List[Task]):
        self.enabled = enabled
        self.timezone = timezone
        self.schedule_interval = schedule_interval
        self.tasks = tasks


class DagConfigSchema(Schema):
    enabled = fields.Bool(required=False, missing=True)
    timezone = fields.Str(required=True)
    schedule_interval = fields.Str(validate=IsValidCron(), missing=None)
    tasks = fields.List(cls_or_instance=fields.Nested(TaskSchema), required=True)

    @post_load
    def make_dag_config(self, data, **kwargs):
        data_with_objects = copy.deepcopy(data)
        tasks = []
        for task in data_with_objects['tasks']:
            task_entity = Task(**task)
            tasks.append(task_entity)

        data_with_objects['tasks'] = tasks
        return DagConfig(**data_with_objects)


def load_dag_schema(payload) -> DagConfig:
    schema = DagConfigSchema()
    result = schema.load(payload)

    if result.errors:
        raise InvalidDagConfig(result.errors)

    return result.data
