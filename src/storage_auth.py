import requests
from urllib.parse import urlencode
import webbrowser
import time
import logging


class BaiduAuth:
    def __init__(self, cg):
        self._update_save = cg.update_save

        baidu_cloud_config = cg.get_baidu_config()

        self.app_id = baidu_cloud_config.get('app_id')
        self.app_key = baidu_cloud_config.get('app_key')
        self.secret_key = baidu_cloud_config.get('secret_key')
        self.sign_key = baidu_cloud_config.get('sign_key')
        self.access_token = baidu_cloud_config.get('access_token')
        self.refresh_token = baidu_cloud_config.get('refresh_token')


    def auth_error_check(self, error_code):
        '''
        api调用的时候，token相关的错误处理
        
        Args:
            response (object) : 错误代码
        '''

        if error_code:
            if error_code == 110: # token不合法，重新获取token
                self._auth_flow()
                return self.access_token
            
            if error_code == 111: # token已过期，刷新
                self._refresh_token()
                return self.access_token
            

    def get_token(self):
        return self.access_token
    

    def _auth_flow(self):
        '''
        获取token的完整流程。
        '''
        # 获取设备码
        device_code, qrcode_url, interval = self._get_authorization_code()

        # 展示授权二维码
        self._show_qrcode(qrcode_url)

        # 轮询获取token
        self._ask_access_token(device_code, interval)

        self._update_key()

        

    def _get_authorization_code(self):
        '''
        Device_code授权方案的第一步，获取设备码、用户码。

        Returns:
            device_code (str) : 设备码
            qrcode_url (str) : 授权二维码的url
            interval (int) : 轮询间隔（秒）
        '''
        # 设置请求参数
        params = {
            'response_type': 'device_code',
            'client_id': self.app_key,
            'scope': 'basic,netdisk',
        }
        api_url = 'https://openapi.baidu.com/oauth/2.0/device/code?'

        # 发送 GET 请求
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            device_code = data.get('device_code')
            qrcode_url = data.get('qrcode_url')
            interval = data.get('interval')
            return device_code, qrcode_url, interval
        else:
            print("请求失败，状态码：", response.status_code)
            return None, None, None
        

    def _show_qrcode(self, qrcode_url):
        
        return webbrowser.open(qrcode_url)



    def _ask_access_token(self, device_code, interval):
        '''
        Device_code授权方案的第二步，轮询10次获取Access Token。
        获取后更新到`self.access_token`
        
        Args:
            device_code (str): 第一步中获取的设备码
            interval (int): 第一步中获取的最小轮询间隔（秒） 
        '''
        logging.debug(f'开始轮询获取Access Token')
        
        # 设置请求参数
        params = {
            'code': device_code,
            'client_id': self.app_key,
            'client_secret': self.secret_key,
        }

        api_url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=device_token&'
        headers = {
        'User-Agent': 'pan.baidu.com'
        }

        loop_count = 0
        while loop_count<10 :
            # 发送 GET 请求
            response = requests.get(api_url, params=params, headers=headers)
            data = response.json()
            logging.debug(f'第 { loop_count } 次轮询响应：\n{ data }')
            
            if 'access_token' in data:
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                logging.debug(f'成功获取 Access Token ')
                return
            
            loop_count += 1
            time.sleep(interval)  # 等待一段时间再次请求

        if 'error' in data:
            raise Exception("Error getting token: " + data['error'])
        else:
            raise Exception('Error: 请求 Access Token 超时')



    def _refresh_token(self):
        '''
        Access Token过期后使用refresh_token进行刷新。
        
        Returns:
            device_code (str): 第一步中获取的设备码
            interval (int): 第一步中获取的最小轮询间隔（秒） 
        '''
        api_url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=refresh_token&'
        params = {
            'refresh_token': self.refresh_token,
            'client_id': self.app_key,
            'client_secret': self.secret_key,
        }
        headers = {
        'User-Agent': 'pan.baidu.com'
        }

        response = requests.get(api_url, params=params, headers=headers)
        data = response.json()

        if 'access_token' in data:
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')
            self._update_key()
            return
            
        elif 'error' in data:
            raise Exception("Error getting token: " + data['error_description'])


    def _update_key(self):
        logging.debug(f'正在更新 Tokens')
        section = 'BaiduCloud'
        updates = {
            'AccessToken' : self.access_token,
            'RefreshToken' : self.refresh_token,
        }

        return self._update_save(section, updates)
    