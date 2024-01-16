import configparser
import threading
import logging


class Config:
    def __init__(self, filename='config.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.config.read(self.filename)
        self.lock = threading.Lock()


    def get_local_config(self):
        section = 'LocalFiles'
        with self.lock:
            return {
                'device_name': self.config.get(section, 'DeviceName', fallback='DefaultDevice'),
                'local_directory': self.config.get(section, 'LocalDirectory', fallback='/default/path'),
                'check_interval': self.config.getint(section, 'CheckInterval', fallback=30)
            }

    def get_baidu_config(self):
        section = 'BaiduCloud'
        with self.lock:
            return {
                'app_id': self.config.get(section, 'AppID', fallback=''),
                'app_key': self.config.get(section, 'AppKey', fallback=''),
                'secret_key': self.config.get(section, 'SecretKey', fallback=''),
                'access_token': self.config.get(section, 'AccessToken', fallback=''),
                'refresh_token': self.config.get(section, 'RefreshToken', fallback=''),
            }
    
    def update_save(self, section, updates):
        '''
        更新配置文件

        Args:
            section (str) : 需要更新的块区
            updates (dic) : 等待更新的字典，注意：字典的 key 要用配置文件的大写模式如：AccessKey
        '''
        with self.lock:
            # 检查区域是否存在，如果不存在，则创建
            if not self.config.has_section(section):
                self.config.add_section(section)

            # 遍历字典并更新配置值
            for key, value in updates.items():
                self.config.set(section, key, value)
                logging.debug(f'正在更新 { key } : { value }')
            # 将更改一次性写回文件
            with open(self.filename, 'w') as configfile:
                logging.debug(f'正在写入配置文件')
                self.config.write(configfile)
            
            logging.info(f"已更新配置文件 {section} 部分")


    def reload(self):
        with self.lock:
            self.config.read(self.filename)


# 创建一个 Config 实例
# config = Config()
