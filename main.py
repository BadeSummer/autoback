import sys
sys.path.append('src')

import status_manager,configer
from queue import Queue
from threading import Thread
import file_checker,file_uploader
import storage_auth
from upload_monitor import UploadMonitor
import logging

def main():
    # logging
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.basicConfig(level=logging.DEBUG, filename='run.log', format='%(asctime)s - %(levelname)s - %(message)s')

    # config
    logging.info(f'加载配置文件')
    config = configer.Config()

    # Global upload task queue.
    logging.info(f'初始化文件上传队列')
    file_queue = Queue()

    # Global status manager
    logging.info(f'初始化状态控制器')
    s_manager = status_manager.StatusManager(file_queue)

    # 传递状态控制器到文件检测和文件上传模块
    logging.info(f'启动文件检测线程')
    file_check_thread = Thread(target=file_checker.check_for_new_files, args=(file_queue, s_manager, config))
    file_check_thread.start()

    # 创建 UploadMonitor 实例
    upload_monitor = UploadMonitor(file_queue, s_manager, config)

    # 开始上传
    logging.info(f'启动文件上传线程')
    upload_monitor.start_monitor()

    upload_monitor.upload_monitor_thread.join()
    file_check_thread.join()

if __name__ == "__main__":
    main()
