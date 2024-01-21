import sys, os
import unittest
from unittest.mock import patch, Mock, MagicMock
import tempfile
from src.storage_auth import BaiduAuth
from config import Config  # 替换为你的模块名
import logging


class TestBaiduAuth(unittest.TestCase):

    def setUp(self):
        # 这里可以进行一些初始化操作

        # 创建临时的配置文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

        temp_config_content = """
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
        self.temp_file.write(temp_config_content.encode())  # 将字符串编码为字节
        self.temp_file.close()

        self.cg = Config(self.temp_file.name)
        self.auth = BaiduAuth(self.cg) 

        # 开启日志
        # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(levelname)s - %(message)s')


    
    def tearDown(self):
        os.remove(self.temp_file.name)


    @patch.object(BaiduAuth, '_refresh_token')
    @patch.object(BaiduAuth, '_auth_flow')
    def test_auth_error_check(self, mock_auth_flow, mock_refresh_token):
        '''测试是否能正确处理错误信息'''

        # 测试110报错，重新获取token
        self.auth.auth_error_check(110)
        mock_auth_flow.assert_called()

        self.auth.auth_error_check(111)
        mock_refresh_token.assert_called()


    def test_get_token(self):
        init_token ='test_access_token'
        got_token = self.auth.get_token()

        self.assertEqual(init_token, got_token)


    @patch('requests.get')
    def test_get_authorization_code(self, mock_get):
        '''测试授权的第一步，获取设备码、用户码'''
        
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'device_code': "mock_device_code",
            'user_code': "mock_user_code",
            'verification_url': "mock_ve_url",
            'qrcode_url': "mock_qrcode_url",
            'expires_in': 300,
            'interval': 5
        }
        mock_get.return_value = mock_response

        # 目标函数
        device_code, qrcode_url, interval = self.auth._get_authorization_code()

        # 检验
        self.assertEqual(device_code, 'mock_device_code')
        self.assertEqual(qrcode_url, 'mock_qrcode_url')
        self.assertEqual(interval, 5)


    @patch('time.sleep', return_value=None)
    @patch('requests.get')
    def test_ask_access_token_polling(self, mock_get, mock_sleep):
        '''测试授权第二步，轮询获得token'''

        # 测试正常获取，10次以内得到token
        # 设置轮询响应
        response_wrong = [
            MagicMock(status_code=200, json=lambda: {'error': 'authorization_pending'}),
        ]
        response_right = [
            MagicMock(status_code=200, json=lambda: {'access_token': 'your_access_token', 'refresh_token': 'your_refresh_token', 'expires_in': 2592000})
        ]

        expect_loop = 5
        mock_get.side_effect = response_wrong * expect_loop + response_right

        # 测试正常获取
        logging.debug(f'测试授权轮询第二步，正常获取token')
        self.auth._ask_access_token('device code', 1)

        # 验证
        self.assertEqual(self.auth.access_token, 'your_access_token')
        mock_sleep.assert_called()

        # 测试获取超时，10次以内都无token
        expect_loop = 12
        mock_get.side_effect = response_wrong * expect_loop + response_right
        
        # 测试超时
        logging.debug(f'测试授权轮询第二步，无法获取token')
        with self.assertRaises(Exception) as cm:
            self.auth._ask_access_token('device code', 1)

        # 验证
        self.assertIn('Error', str(cm.exception), msg=None)


    @patch('requests.get')
    def test_refresh_token(self, mock_get):
        '''测试刷新token'''
        
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'refresh_access_token', 
            'refresh_token': 'refresh_refresh_token', 
            'expires_in': 2592000
        }
        mock_get.return_value = mock_response

        # 目标函数
        self.auth._refresh_token()

        # 检验
        self.assertEqual(self.auth.access_token, 'refresh_access_token')
        self.assertEqual(self.auth.refresh_token, 'refresh_refresh_token')


    def test_update_key(self):
        '''测试是否能更新token'''

        # 确保初始化没有错
        init_access_token = 'test_access_token'
        init_refresh_token = 'test_refresh_token'
        self.assertEqual(init_access_token, self.auth.access_token)
        self.assertEqual(init_refresh_token, self.auth.refresh_token)

        new_access_token = 'new_access_token'
        new_refresh_token = 'new_refresh_token'
        self.auth.access_token = new_access_token
        self.assertEqual(self.auth.access_token, new_access_token)
        self.auth.refresh_token = new_refresh_token

        # 测试
        self.auth._update_key()

        now_config = self.cg.get_baidu_config()
        logging.debug(f'更新后的配置文件：{now_config}')
        config_access_token = now_config.get('access_token')
        config_refresh_token = now_config.get('refresh_token')

        # 验证
        self.assertEqual(new_access_token, config_access_token)
        self.assertEqual(new_refresh_token, config_refresh_token)


if __name__ == '__main__':
    unittest.main()
