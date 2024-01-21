STATUS_NOT_UPLOADED = '未上传'
STATUS_UPLOADED = '已上传'
STATUS_UPLOADING = '正在上传'
from utils import MAIN_LOG

import json
import os
import threading
import logging
mainlog = logging.getLogger(MAIN_LOG)

class StatusManager():
    """
    StatusManager 用于管理文件的上传状态。

    这个类提供了方法来加载、更新、保存和删除特定文件的上传状态。
    状态信息被存储在一个 JSON 文件中。

    Args:
        queue (Queue) : 文件上传的任务队列
        filename (str): 状态文件的名称。默认为 'upload_status.json'

    Methods:
        get_status(file_name) : 获取指定文件的上传状态
        add(file_name) : 增加文件到状态表
        set_uploaded(file_name) : 设置文件状态为 已经上传
        set_uploading(file_name) : 设置文件状态为 正在上传
        set_not_uploaded(file_name) : 设置文件状态为 未上传
        reload_status() : 重新加载状态文件
        remove_status(file_name) : 从状态中删除指定文件的记录
    """

    def __init__(self, queue, filename='upload_status.json'):
        """
        初始化 StatusManager 类的新实例。

        Args:
            filename (str): 状态文件的名称。默认为 'upload_status.json'。
        """
        mainlog.debug(f'正在初始化状态控制器')
        self.lock = threading.Lock()
        self.filename = filename
        self.queue = queue
        self.status = self._load_status()
        
        # 初始化加载状态后同步到任务队列
        mainlog.debug(f'同步未上传状态到队列中')
        self._sync_queue()



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


    def is_exsit(self, file_name):
        '''
        文件是否已经登记
        '''
        return file_name in self.status
    

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
        """ 重新加载状态文件 """
        with self.lock:
            self.status = self._load_status()
            # self._sync_queue()


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


    def _sync_queue(self):
        '''状态为未上传的文件都提交到任务列表，会覆盖原来的任务！'''
        with self.lock:  # 使用互斥锁确保线程安全

            # 通知其他线程这边即将要开始清空：
            self.queue.put(None)

            # 清空当前队列
            while not self.queue.empty():
                self.queue.get()
                self.queue.task_done()

            # 遍历状态，找到所有“未上传”的文件
            for filename, file_status in self.status.items():
                if file_status == STATUS_NOT_UPLOADED or file_status == STATUS_UPLOADING:
                    self.queue.put(filename)


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
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.status, file, indent=4, ensure_ascii=False)


    def _load_status(self):
        """
        加载状态文件。

        从 JSON 文件中读取状态数据。如果文件不存在，则返回一个空字典。

        Returns:
            dict: 包含文件状态的字典。
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return {}