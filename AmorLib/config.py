import os, configparser

# 配置文件路径
CONFIG = "AmorLib/config.ini"

# 检查配置文件是否存在
if not os.path.exists(CONFIG):
    raise FileNotFoundError(f"配置文件 {CONFIG} 不存在")

# 初始化配置解析器
_parser = configparser.ConfigParser()
_parser.read(CONFIG, encoding="utf-8")

_error = (configparser.NoSectionError, configparser.NoOptionError)


class Config:
    @staticmethod
    def get(section, key, default="") -> str:
        try:
            return _parser.get(section, key)
        except _error:
            return default

    @staticmethod
    def getboolean(section, key, default=False) -> bool:
        try:
            return _parser.getboolean(section, key)
        except _error:
            return default


ACCOUNT_PATH = Config.get("path", "account")
DB_PATH = Config.get("path", "db")

CONF_DIR = Config.get("dir", "conf")
DATA_DIR = Config.get("dir", "data")
TMP_DIR = Config.get("dir", "tmp")
