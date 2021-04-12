from abc import ABC, abstractmethod


class OperatorFactory(ABC):
    @classmethod
    @abstractmethod
    def create(cls, operator, dag_config_path, **kwargs):
        """
        This is the OperatorFactory abstract class all other operator factory class must be derived from.
        The purpose of this factory class is to make the config file more light weight with added support such as
        - Jinja Templating Support
        - Pass sql statement as a file
        - Complex and reusable parsing logic that would have been otherwise duplicated

        @param operator: Any class derived from airflow.models.baseoperator.BaseOperator
        @param dag_config_path: Absolute path of the dag config
        @param kwargs: arguments passed through the configuration file from a Task alongside what's required
        by the operator itself
        @return a class instance of an Airflow Operator
        """
        raise NotImplemented


class DefaultOperatorFactory(OperatorFactory):
    @classmethod
    def create(cls, operator, dag_config_path, **kwargs):
        return operator(dag_config_path=dag_config_path, **kwargs)
