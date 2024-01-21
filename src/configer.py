import configparser
import threading
import logging
import os
from utils import MAIN_LOG
mainlog = logging.getLogger(MAIN_LOG)

class Config:
    def __init__(self, filename='config.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser(interpolation=None)

        try:
            f = open(filename)
            f.close()
        except FileNotFoundError:
            example = '''[LocalFiles]\n# 设备名称\ndevicename = 设备名称\n# 本地检测新文件目录\nlocaldirectory = 本地检测目录\n# 检测时间间隔 单位（分钟）\ncheckinterval = 30\n\n[BaiduCloud]\n# 本程序的百度应用\nappname = 摄影素材自动备份\nappid = 47097507\nappkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb\nsecretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6\nsignkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V\n\n# 用户百度授权token，有的话可以输入，无可留空\naccesstoken = \nrefreshtoken = '''
            with open(filename, "w") as f:
                f.write(example)
            mainlog.critical(f'配置文件不存在，已创建模版{filename}')
            raise FileNotFoundError(f'配置文件不存在，已创建模版{filename}')

        mainlog.debug(f'尝试读取配置{filename}')
        self.config.read(self.filename)
        self._check_config_required()

        self.lock = threading.Lock()


    def get_local_config(self):
        section = 'LocalFiles'
        with self.lock:
            return {
                'device_name': self.config.get(section, 'devicename'),
                'local_directory': self.config.get(section, 'localdirectory'),
                'check_interval': self.config.getint(section, 'checkinterval', fallback=30)
            }

    def get_baidu_config(self):
        section = 'BaiduCloud'
        with self.lock:
            return {
                'app_name': self.config.get(section, 'appname', fallback='摄影素材自动备份'),
                'app_id': self.config.get(section, 'appid', fallback='47097507'),
                'app_key': self.config.get(section, 'appkey', fallback='H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb'),
                'secret_key': self.config.get(section, 'secretkey', fallback='pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6'),
                'sign_key' : self.config.get(section, 'signkey', fallback='X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V'),
                'access_token': self.config.get(section, 'accesstoken', fallback=''),
                'refresh_token': self.config.get(section, 'refreshtoken', fallback=''),
            }
    
    def update_save(self, section, updates):
        '''
        更新配置文件

        Args:
            section (str) : 需要更新的块区
            updates (dic) : 等待更新的字典，注意：字典的 key 要用配置文件小写模式如：accesskey
        '''
        with self.lock:
            # 检查区域是否存在，如果不存在，则创建
            if not self.config.has_section(section):
                self.config.add_section(section)

            # 遍历字典并更新配置值
            for key, value in updates.items():
                self.config.set(section, key, value)
                mainlog.debug(f'正在更新 { key } : { value }')
            # 将更改一次性写回文件
            with open(self.filename, 'w') as configfile:
                mainlog.debug(f'正在写入配置文件')
                self.config.write(configfile)
            
            mainlog.info(f"已更新配置文件 {section} 部分")

    def reload(self):
        with self.lock:
            self.config.read(self.filename)

    def _check_config_required(self):
        '''检查配置文件'''
        # 定义必需的配置项
        required_configs = {
            'LocalFiles': ['devicename', 'localdirectory'],
            'BaiduCloud': ['appname', 'appid', 'appkey', 'secretkey']
        }

        # 遍历必需的配置项进行检查
        for section, keys in required_configs.items():
            for key in keys:
                values = self.config.get(section, key, fallback='')
                if values=='':
                    # 如果发现配置项为空，可以选择抛出异常或返回错误信息
                    raise ValueError(f"配置项 {section}.{key} 是必需的，但目前为空。")

        # 所有必需的配置项都存在且非空
        return True

# 创建一个 Config 实例
# config = Config()
