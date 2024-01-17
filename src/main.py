import sys
sys.path.append('src')

import status_manager,config
from queue import Queue
from threading import Thread
import file_checker,file_uploader
import storage_auth
from upload_monitor import UploadMonitor

def main():

    # config
    config = config.Config()

    # Global status manager
    status_manager = status_manager.StatusManager()

    # Global upload task queue.
    file_queue = Queue()

    # 传递状态到文件检测和文件上传模块
    file_check_thread = Thread(target=file_checker.check_for_new_files, args=(file_queue, status_manager, config))
    file_check_thread.start()

    # 创建 UploadMonitor 实例
    upload_monitor = UploadMonitor(file_queue, status_manager, config)

    # 开始上传
    upload_monitor.start_uploading()

    upload_monitor.upload_monitor_thread.join()
    file_check_thread.join()

if __name__ == "__main__":
    main()
