# !/usr/bin/env python3
"""
    xpan upload
    include:
        precreate
        upload
        create
"""
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from pprint import pprint
from openapi_client.api import fileupload_api
import openapi_client

def precreate():
    """
    precreate
    """
    #    Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = fileupload_api.FileuploadApi(api_client)
        access_token = "126.4b3e02c06fb017f9978f561f9cd8a5c6.YgMXMg-H-epCdwlbjeoJJL7YdXdIrrPgLE4i4zO.iY00bA"  # str |
        path = '/apps/摄影素材自动备份/MyTelescope/测试运行/tele1.jpg'  # str | 对于一般的第三方软件应用，路径以 "/apps/your-app-name/" 开头。对于小度等硬件应用，路径一般 "/来自：小度设备/" 开头。对于定制化配置的硬件应用，根据配置情况进行填写。
        isdir = 0  # int | isdir
        size = 281846  # int | size
        autoinit = 1  # int | autoinit
        block_list = '["226112234f8242d733895d77930ae7c9"]' # str | 由MD5字符串组成的list
        rtype = 3  # int | rtype (optional)

        # example passing only required values which don't have defaults set
        # and optional values
        try:
            api_response = api_instance.xpanfileprecreate(
                access_token, path, isdir, size, autoinit, block_list, rtype=rtype)
            pprint(api_response)
        except openapi_client.ApiException as e:
            print("Exception when calling FileuploadApi->xpanfileprecreate: %s\n" % e)


def upload():
    """
    upload
    """
    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = fileupload_api.FileuploadApi(api_client)
        access_token = "121.853f91f14541f053b953c73d8c82411f.YCyzsg2LW4nObIsWaH9pJ3UviHD6aAJPO1r5Ge-.-IXtJA"  # str |
        partseq = "0"  # str |
        path = "/apps/摄影素材自动备份/子目录/a.txt"  # str |
        uploadid = "N1-MjAwMToyNTA6MzAwMjozMjcwOmYwYmQ6NDMzYTo0YTNiOmFjOTY6MTcwNTU2MDY5OTo0MDg2MzkxNjc3NzU0MjQ2MDI="  # str |
        type = "tmpfile"  # str |
        try:
            file = open('./uploadtestdata/a.txt', 'rb') # file_type | 要进行传送的本地文件分片
        except Exception as e:
            print("Exception when open file: %s\n" % e)
            exit(-1)

        # example passing only required values which don't have defaults set
        # and optional values
        try:
            api_response = api_instance.pcssuperfile2(
                access_token, partseq, path, uploadid, type, file=file)
            pprint(api_response)
        except openapi_client.ApiException as e:
            print("Exception when calling FileuploadApi->pcssuperfile2: %s\n" % e)


def create():
    """
    create
    """
    # Enter a context with an instance of the API client
    with openapi_client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = fileupload_api.FileuploadApi(api_client)
        access_token = "121.853f91f14541f053b953c73d8c82411f.YCyzsg2LW4nObIsWaH9pJ3UviHD6aAJPO1r5Ge-.-IXtJA"  # str |
        path = "/apps/摄影素材自动备份/子目录/a.txt"  # str | 与precreate的path值保持一致
        isdir = 0  # int | isdir
        size = 271 # int | 与precreate的size值保持一致
        uploadid = "N1-MjAwMToyNTA6MzAwMjozMjcwOmYwYmQ6NDMzYTo0YTNiOmFjOTY6MTcwNTU2MDY5OTo0MDg2MzkxNjc3NzU0MjQ2MDI="  # str | precreate返回的uploadid
        block_list = '["d05f84cf5340d1ef0c5f6d6eb8ce13b8"]'  # str | 与precreate的block_list值保持一致
        rtype = 3  # int | rtype (optional)

        # example passing only required values which don't have defaults set
        # and optional values
        try:
            api_response = api_instance.xpanfilecreate(
                access_token, path, isdir, size, uploadid, block_list, rtype=rtype)
            pprint(api_response)
        except openapi_client.ApiException as e:
            print("Exception when calling FileuploadApi->xpanfilecreate: %s\n" % e)


if __name__ == '__main__':
    precreate()
    upload()
    create()
