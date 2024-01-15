import unittest
from unittest.mock import Mock, patch
import sys
import os
import time
import logging


# 将 src 目录添加到 sys.path 以便导入 file_checker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import file_checker
from queue import Queue

class TestFileChecker(unittest.TestCase):
    """测试 file_checker 模块的类"""

    def setUp(self):
        """在每个测试前执行，用于设置测试环境"""
        self.queue = Queue()
        self.status_manager = Mock()
        self.config = Mock()
        self.config.get_local_config.return_value = {
            'device_name': 'TestDevice',
            'local_directory': '/test/directory',
            'check_interval': 1
        }
        file_checker.should_continue = True

        # 日志输出
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')


    @patch('time.sleep', return_value=None)
    @patch('os.listdir')
    @patch('os.path.isfile')
    @patch('os.path.getmtime')
    def test_check_for_new_files(self, mock_getmtime, mock_isfile, mock_listdir, mock_sleep):
        """测试 check_for_new_files 函数是否正确处理新文件"""

        # 模拟文件系统
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        mock_getmtime.return_value = 10000

        # 模拟状态管理器
        self.status_manager.get_status.return_value = 'NOT_EXIST'

        # 循环结束控制
        loop_counter = [0]  # 使用列表以便在闭包内修改

        def should_continue():
            loop_counter[0] += 1
            return loop_counter[0] <= 1  # 仅允许循环一次

        # 运行测试的函数
        file_checker.check_for_new_files(self.queue, self.status_manager, self.config, should_continue=should_continue)

        # 验证文件是否被加入队列
        self.assertEqual(self.queue.qsize(), 2)
        self.assertEqual(self.queue.get(), '/test/directory/file1.txt')
        self.assertEqual(self.queue.get(), '/test/directory/file2.txt')

        # 验证状态管理器是否被正确调用
        self.status_manager.get_status.assert_called()
        self.status_manager.add.assert_called()
        file_checker.should_continue = False

        mock_sleep.assert_called()

    
    @patch('time.sleep', return_value=None)
    @patch('os.path.getmtime')
    @patch('os.path.isfile')
    @patch('os.listdir')
    def test_files_after_last_check(self, mock_listdir, mock_isfile, mock_getmtime, mock_sleep):
        # 模拟文件系统
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True

        # 模拟状态管理器
        self.status_manager.get_status.return_value = 'NOT_EXIST'

        last_checked_time = 10000  # 指定 last_checked 时间

        # 循环结束控制
        loop_counter = [0]  # 使用列表以便在闭包内修改

        def should_continue():
            loop_counter[0] += 1
            return loop_counter[0] <= 1  # 仅允许循环一次
        
        # 模拟两个文件的修改时间，一个在 last check 之前，一个在之后
        def getmtime_side_effect(file_path):
            if file_path.endswith('file1.txt'):
                return last_checked_time - 100  # file1 在 last check 之前
            else:
                return last_checked_time + 100  # file2 在 last check 之后

        mock_getmtime.side_effect = getmtime_side_effect

        file_checker.check_for_new_files(self.queue, self.status_manager, self.config, last_checked_time, should_continue=should_continue)

        # 验证只有一个文件被加入队列
        self.assertEqual(self.queue.qsize(), 1)
        self.assertEqual(self.queue.get(), '/test/directory/file2.txt')
        file_checker.should_continue = False


if __name__ == '__main__':
    unittest.main()
