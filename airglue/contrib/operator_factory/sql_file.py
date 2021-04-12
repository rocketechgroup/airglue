import os

from airglue.contrib.operator_factory.default import OperatorFactory


class SqlFileMissingError(ValueError):
    pass


class SqlFileOperatorFactory(OperatorFactory):
    @classmethod
    def create(cls, operator, dag_config_path, **kwargs):
        sql_file_path = kwargs.get('sql_file_path')
        if not sql_file_path:
            raise SqlFileMissingError(f'sql_file_path must be defined')

        sql_file_abs_path = os.path.sep.join([dag_config_path, sql_file_path])
        try:
            with open(sql_file_abs_path, 'r') as fp:
                sql = fp.read()
        except IOError:
            raise SqlFileMissingError(f'Cannot access SQL file `{sql_file_abs_path}`')

        return operator(sql=sql, **kwargs)
