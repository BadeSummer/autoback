import sys
import os

# 获取 project 目录的路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将 external 目录添加到 sys.path
external_path = os.path.join(project_path, 'external/baidusdk')
src_path = os.path.join(project_path, 'src')
sys.path.append(external_path)

from abc import ABC, abstractmethod
from storage_auth import BaiduAuth

from utils import File, FilePreprocessor

# 百度网盘SDK
from openapi_client.api import fileupload_api
import openapi_client

import json
import concurrent.futures
import threading
import logging

class BaseUploader(ABC):
    '''
    上传模块的抽象基类
    '''

    def __init__(self, file_name, config):
        self.name = None
        self.file = File(file_name)
        self.auth = None
        self.config = config

    @abstractmethod
    def start_upload(self, task):
        '''
        开始上传任务
        Args:
            task: 要上传的任务
        Return:
            result : 上传结果成功与否
        '''
        pass

    @abstractmethod
    def stop_upload(self):
        '''
        停止上传任务
        '''
        pass

    @abstractmethod
    def upload_status(self):
        '''
        获取上传状态
        Returns:
            上传状态信息，当前进度
        '''
        pass

class BaiduCloudUploader(BaseUploader):
    '''
    百度云盘上传实现
    '''

    def __init__(self, file_name, config):
        super().__init__(file_name, config)
        self.name = '百度云盘'
        self.auth = BaiduAuth(config)

    def start_upload(self):
        # 百度云盘的上传逻辑
        self.uploading = True
        self.progress = 0 # 进度

        # 百度上传路径 上传路径有限制
        app_name = self.config.get_baidu_config().get('app_name')
        device_name = self.config.get_local_config().get('device_name')
        logging.debug(f'应用名称：{app_name}    望远镜设备名称：{device_name}')

        baidu_path_prefix = os.path.join('/apps', app_name, device_name)
        self.upload_path = os.path.join(baidu_path_prefix, self.file.file_path)

        completed_chunks = 0
        total_chunks = len(self.file.chunks)
        lock = threading.Lock()

        logging.info(f'正在上传{self.file.file_path}')
        
        # 预处理
        logging.debug(f'预处理 {self.file.file_path} ')
        file_preprocessor = FilePreprocessor(self.file)
        file_preprocessor.preprocess()

        # 获取token
        access_token = self.auth.get_token()

        # 预上传
        logging.debug(f'预上传 {self.file.file_path} ')
        uploadid = self._api_precreate(access_token, self.file, self.file.block_list)
        
        # 并发上传分片 (用线程池实现，最大线程为5，暂时不可通过配置文件调节)
        logging.debug(f'分片上传 {self.file.file_path} ')
        retries = 20  # 所有分片共享重试次数
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_chunk = {executor.submit(self._api_chunk_upload, access_token, chunk, uploadid): chunk for chunk in self.file.chunks}
            for future in concurrent.futures.as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    success = future.result()
                    if success:
                        with lock:
                            completed_chunks += 1
                            progress = (completed_chunks / total_chunks) * 100
                            print(f"Progress: {progress:.2f}%")

                    elif retries > 0:
                        # 重试逻辑
                        print(f"Retrying {chunk}...")
                        executor.submit(self._api_chunk_upload, access_token, chunk, uploadid)
                        retries -= 1

                    else:
                        raise Exception(f'{ retries }次重试后，分片上传失败')

                except Exception as e:
                    print(f"Error with {chunk.chunk_path}: {e}")
                    return False
                
                if not self.uploading:
                    print(f"本次上传被停止")
                    return False
                
        # 创建文件
        if self._api_creatfile(access_token, self.file, self.file.block_list, uploadid): 
            # 上传成功
            logging.info(f"成功上传 { self.file.file_path }")
            return True
        return False

    def stop_upload(self):
        '''停止上传'''
        self.uploading = False

    def update_upload_progress(self):
        '''更新上传进度'''
        
    def upload_status(self):
        '''
        获取上传状态
        Returns:
            上传状态信息，当前进度
        '''
        pass


    def _api_precreate(
            self, 
            access_token,
            file,
            block_list,
            isdir = 0,
            autoinit = 1,
            rtype = 2
            ):
        '''预上传 api 封装'''
        logging.debug(f'调用预上传api')

        with openapi_client.ApiClient() as api_client:
            api_instance = fileupload_api.FileuploadApi(api_client)
            path = self.upload_path
            size = file.file_size
            block_list = block_list
            logging.debug(f'预上传参数:\npath:{path}\nisdir:{isdir}\nsize:{size}\nautoinit:{autoinit}\nblock_list:{block_list}')
            try:
                api_response = api_instance.xpanfileprecreate(
                    access_token, path, isdir, size, autoinit, block_list, rtype=rtype)

                # data = json.load(api_response)
                uploadid = api_response.get('uploadid')
                logging.debug(f'获取uploadid：{uploadid}')

                if uploadid:
                    return uploadid
                raise Exception(f'无法获取uploadid')
            
            except openapi_client.ApiException as e:
                raise Exception("Exception when calling FileuploadApi->xpanfileprecreate: %s\n" % e)


    def _api_chunk_upload(
            self,
            access_token,
            chunk,
            uploadid,
            ):
        '''分片上传 api 封装'''
        logging.debug(f'调用分片上传api')
        
        with openapi_client.ApiClient() as api_client:
            api_instance = fileupload_api.FileuploadApi(api_client)

            path = self.upload_path
            partseq = str(chunk.chunk_index)
            type = "tmpfile"

            try:
                file = open(chunk.chunk_path, 'rb') # file_type | 要进行传送的本地文件分片
            except Exception as e:
                print("Exception when open file: %s\n" % e)

            try:
                api_response = api_instance.pcssuperfile2(
                    access_token, partseq, path, uploadid, type, file=file)
                
                # data = json.load(api_response)
                if api_response.get('md5') == chunk.chunk_md5:
                    return 0
                
            except openapi_client.ApiException as e:
                print("Exception when calling FileuploadApi->pcssuperfile2: %s\n" % e)


    def _api_creatfile(
            self,
            access_token,
            file,
            block_list,
            uploadid,
            isdir=0,
            rtype=2
            ):
        '''创建文件 api 封装'''
        logging.debug(f'调用创建文件api')

        with openapi_client.ApiClient() as api_client:
            # Create an instance of the API class
            api_instance = fileupload_api.FileuploadApi(api_client)
            path = self.upload_path
            size = file.file_size
            block_list = block_list

            try:
                api_response = api_instance.xpanfilecreate(
                    access_token, path, isdir, size, uploadid, block_list, rtype=rtype)
                # data = json.load(api_response)
                errno = api_response.get('error')
                md5 = api_response.get('md5')
                size = api_response.get('size')
                re_path = api_response.get('path')

                if errno:
                    raise f'创建{ file.file_path }文件失败 错误码:{errno}'

                # logging.debug(f'文件上传对比：path:{re_path==path}  size:{file.file_size==size}  md5:{file.file_md5==md5}')
                # logging.debug(f'\n本地文件{file.file_path}md5：{file.file_md5}\nAPI返回{re_path}md5：{md5}')
                # if re_path==path and file.file_size==size and file.file_md5==md5:
                return True

            except openapi_client.ApiException as e:
                print("Exception when calling FileuploadApi->xpanfilecreate: %s\n" % e)