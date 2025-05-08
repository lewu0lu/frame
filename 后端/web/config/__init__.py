

from config.ConfigStructure import ConfigRecord
from config.ConfigLoader import ConfigLoader,config
# 额外包一次，减少从外部拿配置的引用长度
MONGO_CONFIG = ConfigRecord(ConfigLoader.get("mongo_collection_config.yaml"))

__all__ = [
    "config",  # 本地配置
    "ENV_TYPE",  # 环境类型
    "MONGO_CONFIG",  # mongo配置
]
