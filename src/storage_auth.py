import sys
import os
import re
import json

# 获取 project 目录的路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将 external 目录添加到 sys.path
external_path = os.path.join(project_path, 'external/baidusdk')
src_path = os.path.join(project_path, 'src')
sys.path.append(external_path)

# 百度网盘SDK
from openapi_client.api import auth_api
import openapi_client


import requests
from urllib.parse import urlencode
import webbrowser
import time
import logging

MAX_REDO = 5
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

        

    def _get_device_code(
            self,
            client_id,
            scope="basic,netdisk",
            redo=[]
            ):
        '''
        Device_code授权方案的第一步，获取设备码、用户码。

        Returns:
            device_code (str) : 设备码
            qrcode_url (str) : 授权二维码的url
            interval (int) : 轮询间隔（秒）
        '''
        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = auth_api.AuthApi(api_client)
            # 设置请求参数
            client_id = client_id

            try:
                api_response = api_instance.oauth_token_device_code(client_id, scope)
                self._check_exception(api_response)

                device_code = api_response.get('device_code')
                qrcode_url = api_response.get('qrcode_url')
                interval = api_response.get('interval')

                return device_code, qrcode_url, interval
            
            except openapi_client.ApiException as e:
                if self._check_exception(e) and len(redo)<MAX_REDO:
                    # 如果可以自己处理
                    self._get_device_code(client_id)
                else:
                    # 无法自己处理
                    raise Exception("Exception when calling AuthApi->oauth_token_device_code: %s\n" % e)

            finally:
                    redo.clear()        
        

    def _show_qrcode(self, qrcode_url):
        
        return webbrowser.open(qrcode_url)



    def _ask_device_token(self,
                         device_code,
                         client_id,
                         client_secret,
                         interval,
                         redo=[]
                         ):
        '''
        Device_code授权方案的第二步，轮询10次获取Access Token。
        获取后更新到`self.access_token`
        
        Args:
            device_code (str): 第一步中获取的设备码
            interval (int): 第一步中获取的最小轮询间隔（秒） 
        '''
        logging.debug(f'开始轮询获取Access Token')

        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = auth_api.AuthApi(api_client)
            # 设置请求参数
            code = device_code
            client_id = client_id
            client_secret = client_secret
            interval = interval

            # 轮询设置
            try:
                api_response = api_instance.oauth_token_device_token(code, client_id, client_secret)
                self._check_exception(api_response)

                if 'access_token' in api_client:
                    self.access_token = api_response.get('access_token')
                    self.refresh_token = api_response.get('refresh_token')
                    logging.info(f'成功获取 Access Token ')
                    return
                
            except openapi_client.ApiException as e:
                if self._check_exception(e) and len(redo)<MAX_REDO:
                    # 如果可以自己处理
                    time.sleep(interval)
                    redo.append(1)
                    self._ask_device_token(code,client_id,client_secret,interval)
                else:
                    # 无法自己处理
                    raise Exception("Exception when calling AuthApi->oauth_token_device_token: %s\n" % e)

            finally:
                    redo.clear()



    def _refresh_token(self,
                       refresh_token,
                       client_id,
                       client_secret,
                       redo=[]):
        '''
        Access Token过期后使用refresh_token进行刷新。
        
        '''
        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = auth_api.AuthApi(api_client)
            # 参数设置
            refresh_token = refresh_token
            client_id = client_id
            client_secret = client_secret

            try:
                api_response = api_instance.oauth_token_refresh_token(refresh_token, client_id, client_secret)
                # self._check_exception(api_response)

                self.access_token = api_response.get('access_token')
                self.refresh_token = api_response.get('refresh_token')
                self._update_key()
                return

            except openapi_client.ApiException as e:
                if self._check_exception(e) and len(redo)<MAX_REDO:
                    redo.append(1)
                    self._refresh_token(self,refresh_token, client_id, client_secret)

                else:
                    raise Exception("Exception when calling AuthApi->oauth_token_refresh_token: %s\n" % e)
            
            finally:
                    redo.clear()




    def _update_key(self):
        logging.debug(f'正在更新 Tokens')
        section = 'BaiduCloud'
        updates = {
            'AccessToken' : self.access_token,
            'RefreshToken' : self.refresh_token,
        }

        return self._update_save(section, updates)
    

    def _check_exception(self, api_exception):
        '''
        处理Auth api返回的错误
        
        Returns:
            bool: 是否可以自己处理'''
        match = re.search(r'HTTP response body: (.+)$', api_exception, re.MULTILINE)

        exception_body = json.loads(match.group(1))
        error = exception_body.get('error')
        errmsg = exception_body.get('errmsg')
        request_id = exception_body.get('request_id')
        
        try:
            '''所有可以自己处理的错误都放在这里。'''

            if error == 'expired_token':
                self._refresh_token
                return True

            if error=='authorization_pending':
                return True
            
            if error=='slow_down':
                time.sleep(5)
                return True
        
        except:
            return False