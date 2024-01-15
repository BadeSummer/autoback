import status_manager,config
from queue import Queue
from threading import Thread
import file_checker,file_uploader
import storage_auth

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

    file_upload_thread = Thread(target=file_uploader.upload_files, args=(file_queue, status_manager, config))
    file_upload_thread.start()

    file_check_thread.join()
    file_upload_thread.join()

if __name__ == "__main__":
    main()
