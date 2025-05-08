import os
import yaml
import configparser
from functools import lru_cache

# 根据环境读取不同的配置文件
ENV_TYPE = os.environ.get("ENV_TYPE", "default")
__TEST__ = ENV_TYPE == "testing"
__RELEASE__ = ENV_TYPE == "formal"

# 配置读取路径
config_path = os.path.join(os.path.dirname(__file__), f"{ENV_TYPE}.ini")
if not os.path.exists(config_path):
    config_path = os.path.join(os.path.dirname(__file__), f"default.ini")

config = configparser.ConfigParser()
config.read(config_path, encoding="utf-8")


class ConfigLoader:
    @staticmethod
    @lru_cache
    def get(path):
        # 拿取同目录配置
        path = os.path.join(os.path.dirname(__file__), path)
        with open(path, "r", encoding="utf-8") as f:
            value = yaml.load(f, Loader=yaml.SafeLoader)
            return value


__all__ = [
    "config",
    "ENV_TYPE",
    "__TEST__",  # 是否测试环境
    "__RELEASE__",  # 是否正式环境
]

if __name__ == "__main__":
    from pprint import pprint

    pprint(config.sections())
