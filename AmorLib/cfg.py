import os
import configparser

# 配置文件路径
CONFIG_PATH = "AmorLib/config.ini"

# 检查配置文件是否存在
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"配置文件 {CONFIG_PATH} 不存在")

# 初始化配置解析器
_cfg = configparser.ConfigParser()
_cfg.read(CONFIG_PATH, encoding="utf-8")


class cfg:
    @staticmethod
    def get(section, key, default="") -> str:
        try:
            return _cfg.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    @staticmethod
    def getboolean(section, key, default=False) -> bool:
        try:
            return _cfg.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default


ACCOUNT_PATH = cfg.get("path", "account")
DB_PATH = cfg.get("path", "db")
