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
from utils import MAIN_LOG
mainlog = logging.getLogger(MAIN_LOG)

from threading import Lock

MAX_REDO_FOR_ASK = 60 # 轮询的最大重复次数
MAX_REDO = 5 # 其他API接口最大的重试次数

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
        self.auth_lock = Lock()


    def auth_error_check(self, error_code):
        '''
        api调用的时候，token相关的错误处理
        
        Args:
            response (object) : 错误代码
        '''
        with self.auth_lock:
            if error_code:
                if error_code == 110: # token不合法，重新获取token
                    self._auth_flow()
                    return self.access_token
                
                if error_code == 111: # token已过期，刷新
                    self._refresh_token()
                    return self.access_token
            

    def get_token(self):
        '''给出一个token'''
        with self.auth_lock:
            mainlog.debug(f'Auth：当前token为{self.access_token}')
            if self.access_token == '':
                mainlog.debug(f'无token')
                self._auth_flow()

            mainlog.debug(f'有token')
            return self.access_token
    
    def renew_token(self):
        with self.auth_lock:
            '''重新弄一个有效token'''
            mainlog.debug('执行renew_token')
            errs = ''
            try:
                try:
                    mainlog.debug(f'尝试刷新Access Token')
                    self._refresh_token(self.refresh_token, self.app_key, self.secret_key)

                except Exception as e:
                    errs = errs + str(e)
                    mainlog.debug(f'尝试重新授权')
                    self._auth_flow()

            except Exception as ee:
                errs = errs + str(ee)
                raise Exception(f'获取新token失败{errs}')


    def _auth_flow(self):
        '''
        获取token的完整流程。
        '''
        mainlog.debug(f'执行_auth_flow')
        
        # 获取设备码
        device_code, qrcode_url, interval = self._get_device_code(self.app_key)

        # 展示授权二维码
        self._show_qrcode(qrcode_url)

        # 轮询获取token
        self._ask_device_token(device_code, self.app_key, self.secret_key, interval)

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
        mainlog.debug(f'执行_get_device_code')
        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = auth_api.AuthApi(api_client)
            # 设置请求参数
            client_id = client_id

            try:
                mainlog.debug(f'请求 device code')
                api_response = api_instance.oauth_token_device_code(client_id, scope)

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
        mainlog.debug(f'开始轮询获取Access Token')

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
                mainlog.info(f'发送第{len(redo)}次 device token 请求')
                api_response = api_instance.oauth_token_device_token(code, client_id, client_secret)

                if 'access_token' in api_response:
                    self.access_token = api_response.get('access_token')
                    self.refresh_token = api_response.get('refresh_token')
                    mainlog.info(f'成功获取 Access Token ')
                    return
                
            except openapi_client.ApiException as e:
                if self._check_exception(e) and len(redo)<MAX_REDO_FOR_ASK:
                    # 如果可以自己处理
                    time.sleep(interval+1)
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
        mainlog.debug(f'执行_refresh_token')
        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = auth_api.AuthApi(api_client)
            # 参数设置
            refresh_token = refresh_token
            client_id = client_id
            client_secret = client_secret

            try:
                api_response = api_instance.oauth_token_refresh_token(refresh_token, client_id, client_secret)

                self.access_token = api_response.get('access_token')
                self.refresh_token = api_response.get('refresh_token')

                mainlog.info(f'第{len(redo)}次 device token 请求成功{self.access_token}')
                self._update_key()
                return True

            except openapi_client.ApiException as e:
                if self._check_exception(e) and len(redo)<MAX_REDO:
                    redo.append(1)
                    self._refresh_token(refresh_token, client_id, client_secret)

                else:
                    raise Exception("Exception when calling AuthApi->oauth_token_refresh_token: %s\n" % e)
            
            finally:
                    redo.clear()




    def _update_key(self):
        mainlog.debug(f'正在更新 Tokens')
        section = 'BaiduCloud'
        updates = {
            'accesstoken' : self.access_token,
            'refreshtoken' : self.refresh_token,
        }

        return self._update_save(section, updates)
    

    def _check_exception(self, api_exception):
        '''
        处理Auth api返回的错误
        
        Returns:
            bool: 是否可以自己处理'''
        mainlog.debug('执行_check_exception')
        match = re.search(r'HTTP response body: (.+)$', str(api_exception), re.MULTILINE)
        mainlog.debug(f'提取Auth 错误信息 match :{match}')

        exception_body = json.loads(match.group(1))
        error = exception_body.get('error')
        errmsg = exception_body.get('errmsg')
        request_id = exception_body.get('request_id')
        
        try:
            '''所有可以自己处理的错误都放在这里。'''
            mainlog.debug('Auth 尝试自我修复')
            if error == 'expired_token':
                mainlog.debug('token 过期')
                self._refresh_token(self.app_key)
                return True

            if error=='authorization_pending':
                mainlog.info('用户未扫二维码完成授权')
                return True
            
            if error=='slow_down':
                mainlog.debug(f'请求速度过快，减慢5秒')
                time.sleep(5)
                return True
        
        except:
            mainlog.debug('Auth 无法自我修复')
            raise Exception(f'error:{error}\nerrmsg:{errmsg}\nrequest_id:{request_id}')