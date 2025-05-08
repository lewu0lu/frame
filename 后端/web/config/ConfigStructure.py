import copy


class ConfigRecord:
    """封装配置类"""

    def __init__(self, data: dict):
        self.__data = data

    def get(self, *args, ret=None):
        """配置专用get方法，链式读取，返回copy"""
        res = self.__data
        for arg in args:
            if isinstance(res, dict):
                res = res.get(arg, ret)
            else:
                return ret
        return copy.deepcopy(res)

    def __repr__(self):
        return self.__data.__repr__()

    def __str__(self):
        return self.__data.__str__()

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __getitem__(self, key):
        return self.get(key)
