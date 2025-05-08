import os
from .base import LockPool,Singleton

root_dir = "./cache"


class FileCacheManager(metaclass=Singleton):
    """管理本地脚本缓存"""
    def __init__(self):
        self.root_dir = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def update_cache_script(self, url, script_file):
        """
        更新缓存脚本
        :param url: 脚本url
        :param script_file: 脚本文件内容
        :return:
        """
        with LockPool.try_get_lock(url):
            path = self.find_cache_script(url)
            if path:
                # 上传新脚本，如果下载过就更新新版本，否则不处理，等到执行时再下载
                file_path = os.path.join(path, "temp.py")
                os.remove(file_path)
                script_file.seek(0)
                script_file.save(file_path)
                print("下载脚本")
                return True
            return None

    def find_cache_script(self, url):
        """
        查找缓存脚本
        :param url: 脚本url
        :return: 脚本路径
        """
        path = self.root_dir + "/" + url
        if os.path.exists(path + "/temp.py"):
            return path
        else:
            return False

    def add_cache_script(self, url, script_file):
        """
        添加缓存脚本
        :param url: 脚本url
        :param script_file: 脚本文件内容
        :return: 脚本路径
        """
        with LockPool.try_get_lock(url):
            path = os.path.join(self.root_dir, url)
            if not os.path.exists(path):
                os.makedirs(path)
                print(path)
            temp_file_path = os.path.join(path, "temp.py")
            with open(temp_file_path, "w", encoding='utf-8', newline='') as f:
                f.write(script_file)
            return temp_file_path


if __name__ == "__main__":
    manager = FileCacheManager()
