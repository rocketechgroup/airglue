import sys
from airglue.contrib.operator_factory.default import OperatorFactory


def example_python_function(**kwargs):
    print('I am the python function!')


class PythonOperatorFactory(OperatorFactory):
    @classmethod
    def create(cls, operator, dag_config_path, **kwargs):
        kwargs['python_callable'] = getattr(sys.modules[__name__], kwargs['python_callable'])
        return operator(**kwargs)
