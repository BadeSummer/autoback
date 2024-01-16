STATUS_NOT_UPLOADED = '未上传'
STATUS_UPLOADED = '已上传'
STATUS_UPLOADING = '正在上传'

import json
import os
import threading

class StatusManager:
    """
    StatusManager 用于管理文件的上传状态。

    这个类提供了方法来加载、更新、保存和删除特定文件的上传状态。
    状态信息被存储在一个 JSON 文件中。

    Attributes:
        filename (str): 用于存储文件状态的 JSON 文件的名称。
        status (dict): 一个字典，包含文件名和其对应的上传状态。
    """

    def __init__(self, filename='upload_status.json'):
        """
        初始化 StatusManager 类的新实例。

        Args:
            filename (str): 状态文件的名称。默认为 'upload_status.json'。
        """
        self.lock = threading.Lock()
        self.filename = filename
        self.status = self._load_status()


    def get_status(self, file_name):
        """
        获取指定文件的上传状态。

        Args:
            file_name (str): 需要查询状态的文件名。

        Returns:
            str: 文件的上传状态。
        """
        with self.lock:
            return self.status.get(file_name, 'NOT_EXIST')


    def add(self, file_name):
        """
        增加文件到状态表

        Args:
            file_name (str): 增加的文件
        """
        with self.lock:
            if file_name in self.status:
                raise ValueError(f"文件 '{file_name}' 的状态已经存在。")
            
            self._set_status(file_name, STATUS_NOT_UPLOADED)
            self._save_status()


    def set_uploaded(self, file_name):
        """
        设置文件状态为已经上传

        Args:
            file_name (str): 需要修改状态的文件
        """
        with self.lock:
            if file_name not in self.status:
                raise ValueError(f"文件 '{file_name}' 的不存在。")
            
            self._set_status(file_name, STATUS_UPLOADED)
            self._save_status()


    def set_uploading(self, file_name):
        """
        设置文件状态为正在上传

        Args:
            file_name (str): 需要修改状态的文件
        """
        with self.lock:
            if file_name not in self.status:
                raise ValueError(f"文件 '{file_name}' 的不存在。")
            
            self._set_status(file_name, STATUS_UPLOADING)
            self._save_status()


    def set_not_uploaded(self, file_name):
        """
        设置文件状态为未上传

        Args:
            file_name (str): 需要修改状态的文件
        """
        with self.lock:
            if file_name not in self.status:
                raise ValueError(f"文件 '{file_name}' 的不存在。")
            
            self._set_status(file_name, STATUS_NOT_UPLOADED)
            self._save_status()


    def reload_status(self):
        """ 重新加载状态文件。 """
        with self.lock:
            self.status = self._load_status()


    def remove_status(self, file_name):
        """
        从状态中删除指定文件的记录。

        如果文件在状态字典中存在，则删除它，并更新文件。

        Args:
            file_name (str): 需要删除状态的文件名。
        """
        with self.lock:
            if file_name in self.status:
                del self.status[file_name]
                self._save_status()


    def _set_status(self, file_name, status):
        """
        设置指定文件的上传状态，并保存更改。

        Args:
            file_name (str): 文件名。
            status (str): 要设置的状态。
        """
        self.status[file_name] = status
        self._save_status()


    def _save_status(self):
        """
        将当前状态保存到文件。

        将 status 字典写入到 JSON 文件中。
        """
        with open(self.filename, 'w') as file:
            json.dump(self.status, file, indent=4)


    def _load_status(self):
        """
        加载状态文件。

        从 JSON 文件中读取状态数据。如果文件不存在，则返回一个空字典。

        Returns:
            dict: 包含文件状态的字典。
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return {}