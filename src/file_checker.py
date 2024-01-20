import os
import time

from utils import get_all_files_in_directory, MAIN_LOG
import logging
mainlog = logging.getLogger(MAIN_LOG)

import sys
sys.path.append('src')



def check_for_new_files(queue, status_manager, config, last_checked=None, should_continue=lambda: True):
    """
    检查新文件并将它们加入上传队列。

    Args:
        queue (Queue): 用于添加上传任务的队列。
        status_manager (StatusManager): 状态管理器实例，用于检查文件状态。
        directory (str): 要检查的目录。
        interval (int): 检查间隔时间（分钟）。
    """

    local_config = config.get_local_config()
    device_name = local_config.get('device_name')
    directory = local_config.get('local_directory')
    interval = int(local_config.get('check_interval'))

    mainlog.info("开始检查新文件")

    while should_continue():
        try:
            # 获取目录中的所有文件
            files = get_all_files_in_directory(directory)
            mainlog.info(f"检查目录 {directory} 中的文件")
            mainlog.debug(f"总共发现 {len(files)} 个文件")

            add_count = 0

            for file in files:
                mainlog.debug(f"正在处理 {file} 文件")

                # 只处理文件
                if os.path.isfile(file):
                    # 检查文件的上次修改时间
                    last_modified = os.path.getmtime(file)
                    mainlog.debug(f"{file} 文件的最后修改时间为 {last_modified}")

                    if not status_manager.is_exsit(file):
                        # 如果不存在状态表里，说明是新增的
                        if status_manager.get_status(file) == 'NOT_EXIST':
                            mainlog.debug(f"正在添加 {file} 文件")
                            queue.put(file)
                            status_manager.add(file)
                            add_count += 1
                            mainlog.info(f" {file} 添加完毕")
                        else:
                            mainlog.debug(f" {file} 文件已存在")
        
        except Exception as e:
            # 日志记录异常
            mainlog.ERROR(f"Error checking files: {e}")

        # 上次检查时间有10分钟冗余，避免在循环过程中产生新的文件导致错过。
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mainlog.debug(f"更新最后一次检查时间{ local_time }")

        time.sleep(interval * 60)
        mainlog.info(f"本轮扫描结束，本次新增 {add_count} 个文件进入待上传列表")

