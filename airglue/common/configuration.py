import os

PROJECT_NAME = 'airglue'


class EnvConfig:
    def __init__(self):
        pass

    @property
    def src_path(self):
        return os.environ['AIRGLUE_SRC_PATH']

    @property
    def pull_secret_name(self):
        return os.environ.get('AIRGLUE_PULL_SECRET_NAME', None)

    @property
    def config_path(self):
        return os.environ['AIRGLUE_CONFIG_PATH']


env_config = EnvConfig()
