from abc import ABC, abstractmethod

class BaseUploader(ABC):
    '''
    上传模块的抽象基类
    '''

    def __init__(self):
        self.name = None
        self.task = None

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

    def __init__(self):
        super().__init__()
        self.name = '百度云盘'

    def start_upload(self, task):
        # 百度云盘的上传逻辑
        self.task = task

    def stop_upload(self):
        # 停止上传逻辑
        pass

    def upload_status(self):
        # 获取上传状态逻辑
        pass
