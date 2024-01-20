import sys
sys.path.append('src')

import status_manager,configer
from queue import Queue
import storage_auth

from file_checker import FileChecker
from upload_monitor import UploadMonitor
import logging
from utils import logging_with_terminal_and_file, set_shutdown

def main():
    # logging
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')
    mainlog = logging_with_terminal_and_file()

    # config
    mainlog.info(f'加载配置文件')
    config = configer.Config()

    # Global upload task queue.
    mainlog.info(f'初始化文件上传队列')
    file_queue = Queue()

    # Global status manager
    mainlog.info(f'初始化状态控制器')
    s_manager = status_manager.StatusManager(file_queue)

    # 创建 FileChecker 实例
    mainlog.info('初始化文件夹更新监控')
    file_checker = FileChecker(file_queue, s_manager, config)

    # 创建 UploadMonitor 实例
    mainlog.info(f'初始化上传监控')
    upload_monitor = UploadMonitor(file_queue, s_manager, config)

    # 开始检测
    mainlog.info(f'启动文件检测线程')
    file_checker.star_check()

    # 开始上传
    mainlog.info(f'启动文件上传线程')
    upload_monitor.start_monitor()

    try:
        mainlog.debug('主程序等待线程运行')
        file_checker.check_new_file_thread.join()
        upload_monitor.upload_monitor_thread.join()
    except KeyboardInterrupt:
        mainlog.info('收到Ctrl + C，正在关闭程序')
        set_shutdown()

        file_checker.check_new_file_thread.join()
        mainlog.info('停止文件检测')

        mainlog.info('正在结束上传任务')
        upload_monitor.upload_monitor_thread.join()
        mainlog.info('停止上传')
        

        mainlog.info('程序退出')

if __name__ == "__main__":
    main()
