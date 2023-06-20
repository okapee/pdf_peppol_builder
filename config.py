import os
from pathlib import Path

basedir = Path(__file__).parent.parent


class BaseConfig:
    """
    BaseConfigクラス
    """

    SECRET_KEY = os.environ["SECRET_KEY"]
    WTF_CSRF_SECRET_KEY = os.environ["WTF_CSRF_SECRET_KEY"]


class LocalConfig(BaseConfig):
    """
    BaseConfigクラスを継承してLocalConfigクラスを作成する
    """

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class ProductionConfig(BaseConfig):
    """
    BaseConfigクラスを継承してProductionConfigクラスを作成する
    """

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'prd.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


# config辞書にマッピングする
config = {
    "local": LocalConfig,
    "prd": ProductionConfig,
}