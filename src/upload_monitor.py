import sys
sys.path.append('src')
from file_uploader import *
from threading import Thread
from queue import Empty

import logging
from utils import MAIN_LOG
mainlog = logging.getLogger(MAIN_LOG)


class UploadMonitor:
    '''
    用来监控管理上传任务队列的类

    持续监控上传任务队列里面的任务情况，从队列中提取出一个上传任务，然后
    顺便更新一下任务的状态，随后交给上传工具进行上传。

    Args:
        file_queue (Queue) : 需要监控的队列
        status_manager (StatusManager) : 任务状态管理器
        config (Config) : 配置管理器
        uploader (Uploader): 上传工具，默认是百度网盘`BaiduCloudUploader`

    Methods:
        start_monitor(): 启动监控线程，开始处理上传任务。
        stop_monitoring(): 发送停止信号，停止监控线程。
    '''
    def __init__(self, file_queue, status_manager, config):
        self.file_queue = file_queue # 任务列表
        self.status_manager = status_manager # 状态管理器
        self.config = config # 配置文件管理器
        self._stop_monitoring = False # 
        # self.uploader = uploader

    def start_monitor(self):
        self.upload_monitor_thread = Thread(target=self._upload_files)
        self.upload_monitor_thread.start()

    def stop_monitoring(self):
        self._stop_monitor = True

    def _upload_files(self):
        
        mainlog.info(f'开始监控上传任务')
        while not self._stop_monitoring:
            try:
                # 尝试从队列中获取任务，最多等待一定时间
                mainlog.debug(f'从队列中提取任务')
                task = self.file_queue.get(timeout=5)
                mainlog.debug(f'提取完毕')

                # 检查是否是特殊的停止信号（放在队列里面的None信号）
                if task is None:
                    self._stop_monitoring = True
                    break

                # 处理上传任务
                # 设置正在上传状态
                mainlog.debug(f'设置任务状态为正在上传')
                self.status_manager.set_uploading(task)

                # 创建上传器
                mainlog.debug(f'创建上传器')
                self.uploader = BaiduCloudUploader(task, self.config)

                # 开始上传
                uploaded = self.uploader.start_upload()

                # 处理上传结果
                if uploaded:
                    self.status_manager.set_uploaded(task)
                else:
                    self.status_manager.set_not_uploaded(task)

                self.file_queue.task_done()

            except Empty:
                # 队列空闲，继续检查停止条件
                '''相当于空闲时60秒检测一次是否有停止监控的信号'''
                mainlog.debug('上传队列空闲中...')
                continue

        return "Upload stoped"
