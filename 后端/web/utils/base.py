import queue
import random
import re
import threading
import time
import importlib
import ast


class Singleton(type):
    """
    单例模式
    """
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._single_lock:
                if cls._instance:
                    return cls._instance

                instance = super().__call__(*args, **kwargs)
                cls._instance = instance

        return cls._instance

    def __new__(cls, *args, **kwargs):
        class_obj = super().__new__(cls, *args, **kwargs)
        class_obj._single_lock = threading.Lock()
        return class_obj

    def clear_singleton(self):
        """清除单例"""
        with self._single_lock:
            self._instance = None


class ThreadSingleMeta(type):
    """
    单例模式，使用线程锁
    """
    _instance = {}

    def __call__(cls, *args, **kwargs):
        tid = threading.current_thread().ident

        if not cls._instance.get(tid):
            with cls._single_lock:
                if not cls._instance.get(tid):
                    cls._instance[tid] = super().__call__(*args, **kwargs)
        return cls._instance[tid]

    def __new__(cls, *args, **kwargs):
        class_obj = super().__new__(cls, *args, **kwargs)
        class_obj._single_lock = threading.Lock()
        return class_obj

    def clear_singleton(self):
        with self._single_lock:
            self._instance = {}


def single_cache(timeout):
    """
    计时缓存

    暂时只给固定的信息获取接口使用
    todo 优化
    """

    def decorator(func):
        cache = {}

        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key in cache and time.time() - cache[key]["time"] < timeout:
                return cache[key]["value"]
            result = func(*args, **kwargs)
            cache[key] = {"value": result, "time": time.time()}
            return result

        return wrapper

    return decorator


def subprocess_run(cmd):
    """
    运行子进程，并返回结果
    """
    import shlex
    import subprocess

    if isinstance(cmd, str):
        cmd = shlex.split(cmd)

    assert isinstance(cmd, list)
    print("SubProcess run:\n", " ".join(cmd))
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    print(f"SubProcess Return code: {result.returncode}")
    print(f"SubProcess Output:\n{result.stdout}")
    print(f"SubProcess Error Output:\n{result.stderr}")
    return result


def convert_path(path):
    """
    将路径中的 / 替换为 .
    """
    temp_path = path.replace('/', '.')
    # 去掉最前面的点
    module_path = temp_path.lstrip('.')
    return module_path


def import_attribute(module_path: str):
    """
    返回给定模块路径的属性值
    :param module_path: 句点分割的属性路径，形如path.to.func
    :type module_path: str
    :return: 从路径导入的模块的属性
    :rtype: Any
    """
    # 缓存的键是脚本的url，值是模块
    attribute_path = convert_path("./cache/" + module_path) + ".temp"
    name_bits = attribute_path.split(".")
    module_name_bits, attribute_bits = name_bits[:], []
    module = None
    while len(module_name_bits):
        try:
            module_name = ".".join(module_name_bits)
            module = importlib.import_module(module_name)
            break
        except Exception as e:
            print("error", e)
            attribute_bits.insert(0, module_name_bits.pop())

    if module is None:
        # 尝试内置类型
        try:
            return __builtins__[attribute_path]
        except KeyError:
            raise ValueError("Invalid attribute name: %s" % attribute_path)

    if not attribute_bits:
        return module

    attribute_name = ".".join(attribute_bits)
    if hasattr(module, attribute_name):
        return getattr(module, attribute_name)

    # 静态方法
    attribute_name = attribute_bits.pop()
    attribute_owner_name = ".".join(attribute_bits)
    try:
        attribute_owner = getattr(module, attribute_owner_name)
    except:
        raise ValueError("Invalid attribute name: %s" % attribute_name)

    if not hasattr(attribute_owner, attribute_name):
        raise ValueError("Invalid attribute name: %s" % attribute_name)
    return getattr(attribute_owner, attribute_name)


class LockPool:
    """
    锁池,用于管理多个线程的锁
    """
    __PoolLock = threading.Lock()
    lock_collection = queue.Queue()
    lock_record = {}

    class SgLock:
        """
        锁对象，用于管理一个线程的锁
        """
        def __init__(self):
            self.__lock = threading.Lock()
            self.pool_sign = None

        def renew(self, key):
            self.pool_sign = key

        def __enter__(self):
            """
            获取锁
            """
            self.__lock.acquire()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            释放锁，并且从锁池中移除
            """
            self.__lock.release()
            LockPool.remove_lock(self)

    @classmethod
    def __get_lock(cls, key):
        """
        从锁池中获取一个锁
        :param key: 锁的标识
        :return: 锁对象
        """
        if cls.lock_collection.empty():
            cls.lock_collection.put(cls.SgLock())
        res = cls.lock_collection.get()
        res.renew(key)
        cls.__register_lock(res)
        return res

    @classmethod
    def try_get_lock(cls, key, timeout=3):
        """
        尝试从锁池中获取一个锁
        :param key: 锁的标识
        :param timeout: 超时时间
        :return: 锁对象
        """
        while timeout > 0:
            with cls.__PoolLock:
                if key not in cls.lock_record:
                    lock = cls.__get_lock(key)
                    return lock
            sleep_time = random.uniform(0.1, 0.5)
            time.sleep(sleep_time)
            timeout -= sleep_time
        print(f"\nget lock from collection timeout")
        raise TimeoutError(f"锁争用超时，争用类型：{key}")

    @classmethod
    def __register_lock(cls, lock: SgLock):
        """
        注册一个锁，然后将锁放入锁池中
        """
        cls.lock_record[lock.pool_sign] = lock

    @classmethod
    def remove_lock(cls, lock: SgLock):
        """
        从锁池中移除一个锁
        """
        with cls.__PoolLock:
            cls.lock_record.pop(lock.pool_sign, None)
            cls.lock_collection.put(lock)


class BaseExtractor(ast.NodeVisitor):
    """
    基类，抽取函数参数的类型和值
    """
    def _get_type(self, node):
        """
        获取变量的类型
        :param node: ast.Node
        :return: 变量类型
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return self._get_type(node.value)
        return 'Any' # 如果变量没注释类型也没有默认值，类型就是Any

    def _get_value(self, node):
        """
        获取变量的值
        :param node: ast.Node
        :return: 变量值
        """
        if isinstance(node, (ast.Str, ast.Constant)):
            return node.s if isinstance(node, ast.Str) else node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, (ast.List, ast.Tuple)):
            return type(node.elts)(self._get_value(el) for el in node.elts)
        elif isinstance(node, ast.Dict):
            return {self._get_value(k): self._get_value(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.Call):
            return 'NotNone'  # 如果不是以上类型，也不为空，那可能是某种方法，标记成NotNone
        return None

    def _infer_type_from_value(self, value):
        """
        根据变量的值，推断出变量的类型
        :param value: 变量的默认值
        :return: 变量的类型
        """
        type_map = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            list: 'list',
            dict: 'dict',
            tuple: 'tuple'
        }
        return type_map.get(type(value), 'Any')


class FunctionExtractor(BaseExtractor):
    """
    抽取函数参数的类型和值
    """
    def __init__(self, function_name):
        self.function_name = function_name
        self.function_node = None

    def visit_FunctionDef(self, node):
        """
        遍历函数节点，找到指定的函数节点,然后再解析这个函数节点
        """
        if node.name == self.function_name:
            self.function_node = node
        self.generic_visit(node)

    def extract_parameters(self):
        """
        解析函数参数
        :return: 函数参数列表
        """
        if not self.function_node:
            return None

        parameters = []
        for i, arg in enumerate(self.function_node.args.args):
            param_name = arg.arg
            param_default = self._get_default_value(i)
            param_type = self._get_type(arg.annotation) if arg.annotation else self._infer_type_from_value(
                param_default)

            parameters.append({
                'name': param_name,
                'type': param_type,
                'default': param_default
            })

        return parameters

    def _get_default_value(self, index):
        """
        获取函数参数的默认值
        :param index: 参数索引
        :return: 参数默认值
        """
        defaults = self.function_node.args.defaults
        if index >= len(self.function_node.args.args) - len(defaults):
            return self._get_value(defaults[index - (len(self.function_node.args.args) - len(defaults))])
        return None


class ClassIOExtractor(BaseExtractor):
    """
    抽取OutputParameter类的属性
    """
    def __init__(self):
        self.classes = {}

    def visit_ClassDef(self, node):
        """
        遍历OutputParameter类节点，然后再解析这个类节点
        :param node: ast.Node
        :return: 类属性列表
        """
        if node.name == 'OutputParameter':
            attributes = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    attr_name = item.target.id
                    attr_value = self._get_value(item.value) if item.value else None
                    attr_type = self._get_type(item.annotation) if item.annotation else self._infer_type_from_value(
                        attr_value)
                    attributes.append({'name': attr_name, 'type': attr_type, 'default': attr_value})
            self.classes[node.name] = attributes
        self.generic_visit(node)


def extract_main_function_parameters(file):
    """
    判断是否有main，有则抽取main函数的参数
    :param file: 文件对象
    :return: 参数列表
    """
    file.seek(0)
    content = file.read()
    tree = ast.parse(content)

    extractor = FunctionExtractor('main')
    extractor.visit(tree)

    if not extractor.function_node:
        return None

    return extractor.extract_parameters()


def extract_class_io(file):
    """
    抽取OutputParameter类的属性
    :param file: 文件对象
    :return: 类属性列表
    """
    file.seek(0)
    content = file.read()
    tree = ast.parse(content)

    extractor = ClassIOExtractor()
    extractor.visit(tree)

    return extractor.classes.get("OutputParameter", [])

def validate_path(script_path):
    """
    检查url是否合法
    """
    pattern = re.compile(r'^[a-zA-Z0-9\-_.~/]+$')
    return bool(pattern.match(script_path))


if __name__ == "__main__":
    with open("test.py", "r") as file:
        try:
            params = extract_main_function_parameters(file)
            if params:
                print("main 方法参数:")
                for param in params:
                    print(f"参数名: {param['name']}, 类型: {param['type']}, 默认值: {param['default']}")
            else:
                print("main 方法没有参数")
        except ValueError as e:
            print(e)

