LOCAL_CONFIG_SECTION = 'LocalFiles'
BAIDU_CONFIG_SECTION = 'BaiduCloud'

import os

def get_all_files_in_directory(directory):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # 拼接完整的文件路径
            full_path = os.path.join(dirpath, filename)
            all_files.append(full_path)
    return all_files
