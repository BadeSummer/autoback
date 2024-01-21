import unittest
import tempfile
import os
import json
from queue import Queue
from src.status_manager import StatusManager, STATUS_NOT_UPLOADED, STATUS_UPLOADED, STATUS_UPLOADING  # 请替换为你的模块名

class TestStatusManager(unittest.TestCase):

    def setUp(self):
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

        initial_status = {
            "file1": STATUS_NOT_UPLOADED,
            "file2": STATUS_UPLOADED,
            "file3": STATUS_UPLOADING
        }

        with open(self.temp_file.name, 'w') as file:
            json.dump(initial_status, file)

        self.temp_file.close()

        # 创建临时空队列
        self.test_queue = Queue()

        self.manager = StatusManager(self.test_queue, self.temp_file.name)


    def tearDown(self):
        # 测试完成后删除临时文件
        os.remove(self.temp_file.name)


    # 测试
    def test_load_status(self):
        # 测试加载状态
        status1 = self.manager.get_status("file1")
        self.assertEqual(status1, STATUS_NOT_UPLOADED)

        status2 = self.manager.get_status("file2")
        self.assertEqual(status2, STATUS_UPLOADED)

        status3 = self.manager.get_status("file3")
        self.assertEqual(status3, STATUS_UPLOADING)

        status4 = self.manager.get_status("file4")
        self.assertEqual(status4, 'NOT_EXIST')



    def test_add(self):
        # 新发现一个未上传文件，要更新到状态里面去。
        init_len = len(self.manager.status)

        new_file = 'new_file'
        self.manager.add(new_file)

        new_len = len(self.manager.status)
        new_file_status = self.manager.get_status(new_file)

        # 正常添加新文件应该 字典key + 1，初始状态为未上传
        self.assertEqual(new_len, init_len+1)
        self.assertEqual(new_file_status, STATUS_NOT_UPLOADED)

        # 重新加载，检查add函数是否正确保存
        self.manager.reload_status()
        reload_status = self.manager.get_status(new_file)
        self.assertEqual(reload_status, STATUS_NOT_UPLOADED)

        # 再次添加已存在文件应该会给出报错
        with self.assertRaises(ValueError) as cm:
            self.manager.add(new_file)

        self.assertEqual(str(cm.exception), f"文件 '{new_file}' 的状态已经存在。")
        self.assertEqual(new_len, len(self.manager.status))


    def test_set_status(self):
        # 测试各种设置状态

        # 设置成已上传
        self.manager.set_uploaded('file1')
        f1_status_now = self.manager.get_status('file1')
        
        self.assertEqual(f1_status_now, STATUS_UPLOADED)

        # 重新加载，检查add函数是否正确保存
        self.manager.reload_status()
        reload_status = self.manager.get_status('file1')
        self.assertEqual(reload_status, f1_status_now)


        # 设置成正在上传
        self.manager.set_uploading('file1')
        f1_status_now = self.manager.get_status('file1')
        
        self.assertEqual(f1_status_now, STATUS_UPLOADING)

        # 重新加载，检查add函数是否正确保存
        self.manager.reload_status()
        reload_status = self.manager.get_status('file1')
        self.assertEqual(reload_status, f1_status_now)


        # 设置成未上传
        self.manager.set_not_uploaded('file1')
        f1_status_now = self.manager.get_status('file1')
        
        self.assertEqual(f1_status_now, STATUS_NOT_UPLOADED)


        # 文件不存在
        with self.assertRaises(ValueError) as cm:
            no_f = 'not_exist_file'
            self.manager.set_uploaded(no_f)

        self.assertEqual(str(cm.exception), f"文件 '{no_f}' 的不存在。")
        


    def test_reload_status(self):
        # 外部修改了status文件之后，reload可以更新
        write_by_external = {
            'file1' : STATUS_UPLOADED
        }
        with open(self.temp_file.name, 'w') as file:
            json.dump(write_by_external, file)
        
        # 重新加载
        self.manager.reload_status()
        f1_status = self.manager.get_status('file1')
        f2_status = self.manager.get_status('file2')

        self.assertEqual(f1_status, STATUS_UPLOADED)
        self.assertEqual(f2_status, 'NOT_EXIST')


    def test_recover_queue(self):
        '''测试status对queue的同步操作'''
        
        # 测试初始化同步
        task_init = self.test_queue.get(timeout=5)
        self.test_queue.task_done()
        self.assertEqual(task_init, 'file1')
        self.assertTrue(self.test_queue.empty())

        # 新增一个状态，不会影响queue
        task_new = 'new_task'
        self.manager.add(task_new)
        self.assertTrue(self.test_queue.empty())

        '''测试重新加载是否会同步队列的行为，根据需求选择其中一个测试'''
        
        '''重新加载不执行 同步队列'''
        self.manager.reload_status()
        self.assertTrue(self.test_queue.empty())

        # '''重新加载执行 同步队列'''
        # self.manager.reload_status()
        # self.assertFalse(self.test_queue.empty())
        # task_init = self.test_queue.get(timeout=5)
        # self.test_queue.task_done()
        # self.assertEqual(task_init, 'file1')
        # self.assertTrue(self.test_queue.empty())


if __name__ == '__main__':
    unittest.main()
