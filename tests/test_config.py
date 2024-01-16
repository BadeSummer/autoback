import os
import tempfile
import unittest
from unittest.mock import patch
from src.config import Config  # 请替换为你的模块名

class TestConfig(unittest.TestCase):

    def setUp(self):
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        config_content = """
        [LocalFiles]
        DeviceName=TestDevice
        LocalDirectory=/test/path
        CheckInterval=5

        [BaiduCloud]
        AppID=test_app_id
        AppKey=test_app_key
        SecretKey=test_secret_key
        AccessToken=test_access_token
        RefreshToken=test_refresh_token
        """
        self.temp_file.write(config_content.encode())  # 将字符串编码为字节
        self.temp_file.close()

        self.config = Config(self.temp_file.name)


    def tearDown(self):
        # 测试完成后删除临时文件
        os.remove(self.temp_file.name)


    def test_get_local_config(self):
        # 测试获取本地配置
        local_config = self.config.get_local_config()
        self.assertIn('device_name', local_config)
        # 添加更多断言来验证值


    def test_get_baidu_config(self):
        # 测试获取百度云配置
        baidu_config = self.config.get_baidu_config()
        self.assertIn('app_id', baidu_config)
        # 添加更多断言来验证值


    def test_update_save(self):
        section = 'BaiduCloud'
        updates = {
            'AccessToken' : 'new_token',
            'RefreshToken' : 'new_refresh_token'
        }

        # 测试目标函数
        self.config.update_save(section, updates)

        # 验证
        # 当前config实例内存已经成功更新
        ac_now = self.config.get_baidu_config().get('access_token')
        re_now = self.config.get_baidu_config().get('refresh_token')
        self.assertEqual(ac_now, 'new_token')
        self.assertEqual(re_now, 'new_refresh_token')

        # 重新加载文件中的值，也能正确更新。
        self.config.reload()
        ac_reload = self.config.get_baidu_config().get('access_token')
        re_reload = self.config.get_baidu_config().get('refresh_token')
        self.assertEqual(ac_reload, 'new_token')
        self.assertEqual(re_reload, 'new_refresh_token')


    # 其他测试方法...

if __name__ == '__main__':
    unittest.main()
