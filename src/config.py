import configparser

class Config:
    def __init__(self, filename='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(filename)

    def get_local_config(self):
        return {
            'device_name': self.config.get('LocalFiles', 'DeviceName', fallback='DefaultDevice'),
            'local_directory': self.config.get('LocalFiles', 'LocalDirectory', fallback='/default/path'),
            'check_interval': self.config.getint('LocalFiles', 'CheckInterval', fallback=30)
        }

    def get_baidu_config(self):
        return {
            'app_id': self.config.get('BaiduCloud', 'AppID', fallback=''),
            'app_key': self.config.get('BaiduCloud', 'AppKey', fallback=''),
            'secret_key': self.config.get('BaiduCloud', 'SecretKey', fallback=''),
            'sign_key': self.config.get('BaiduCloud', 'SignKey', fallback='')
        }

# 创建一个 Config 实例
config = Config()
