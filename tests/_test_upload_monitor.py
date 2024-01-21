import unittest
from unittest.mock import Mock, patch
from queue import Queue, Empty
from src.upload_monitor import UploadMonitor  # 替换为您的实际模块路径

class TestUploadMonitor(unittest.TestCase):
    def setUp(self):
        self.queue = Queue()
        self.status_manager = Mock()
        self.config = Mock()
        self.uploader = Mock()
        self.monitor = UploadMonitor(self.queue, self.status_manager, self.config, self.uploader)

    def test_initialization(self):
        self.assertFalse(self.monitor._stop_monitoring)
        self.assertIs(self.queue, self.monitor.file_queue)
        self.assertIs(self.status_manager, self.monitor.file_queue)
        self.assertIs(self.queue, self.monitor.file_queue)
        self.assertIs(self.queue, self.monitor.file_queue)

    @patch('threading.Thread.start')
    def test_start_monitor(self, mock_start):
        self.monitor.start_monitor()
        mock_start.assert_called_once()

    def test_stop_monitoring(self):
        msg = self.monitor.start_monitor()
        self.monitor.stop_monitoring()

        # 验证
        self.assertTrue(self.monitor._stop_monitoring)
        self.assertEqual(msg, "Upload stoped")

    def test_get_and_upload(self):
        '''测试队列处理和状态更新'''

        # 初始任务队列
        test_tasks = ['t1', 't2', 't3']
        for task in test_tasks:
            self.queue.put(task)

        def uploader_side_effect(task):
            if task == 't3':
                self.monitor._stop_monitoring = True
            return True  # 假设上传总是成功

        # 设置 uploader 的 side_effect
        self.uploader.start_upload.side_effect = uploader_side_effect

        self.monitor.start_monitor()
        self.monitor.upload_thread.join(timeout=10)

        # 验证
        # 上传调用了3次
        self.assertEqual(self.uploader.start_upload.call_count, 3)
        # 状态管理器也正确调用
        self.assertEqual(self.status_manager.set_uploading.call_count, 3)
        self.assertEqual(self.status_manager.set_uploaded.call_count, 3)


    def test_stop_by_queue(self):
        '''测试响应队列中给的停止信号'''
        # 初始任务队列
        test_tasks = ['t1', None]
        for task in test_tasks:
            self.queue.put(task)

        self.monitor.start_monitor()
        self.monitor.upload_thread.join(timeout=10)

        # 验证
        self.assertEqual(self.uploader.start_upload.call_count, 1)

        self.assertTrue(self.uploader._stop_monitor)

    @patch('queue.Queue.get', side_effect=Empty)
    def test_check_stop_when_empty(self, mock_get):
        expect_count = 5
        call_count = 0
        def get_side_effect():
            nonlocal call_count
            nonlocal expect_count
            call_count += 1

            if call_count > expect_count:
                self.uploader.stop_monitoring()
                return Empty
            
            return Empty
        
        self.monitor.start_monitor()
        self.monitor.upload_thread.join(timeout=10)

        # 验证
        self.assertEqual(mock_get.call_count, expect_count)


if __name__ == '__main__':
    unittest.main()
