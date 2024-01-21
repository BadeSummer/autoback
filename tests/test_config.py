import sys, os
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_path, 'src')
sys.path.append(src_path)

from configer import Config
import pytest

@pytest.fixture
def temp_config_file_of_normal_options(tmp_path):
    '''正常的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = testdevice
            localdirectory = /test/path
            checkinterval = 30

            [BaiduCloud]
            appname = 摄影素材自动备份
            appid = 47097507
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = 126.d4e31b6a2fb2281af4aa25ad6ee50999.YneUfftF6NPRxSiZZWRbLGhizfGyGV2S4lMuDyn.FeoBYA
            refreshtoken = 127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ
            ''')
    yield temp_file  

@pytest.fixture
def temp_config_file_of_missing_required_options(tmp_path):
    '''缺少必要参数的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = 
            localdirectory = /test/path
            checkinterval = 30

            [BaiduCloud]
            appname = 摄影素材自动备份
            appid = 47097507
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = 126.d4e31b6a2fb2281af4aa25ad6ee50999.YneUfftF6NPRxSiZZWRbLGhizfGyGV2S4lMuDyn.FeoBYA
            refreshtoken = 127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ
            ''')
    yield temp_file  # 这将是你的测试配置文件
    # 测试完成后，文件会自动删除，无需手动清理

@pytest.fixture
def temp_config_file_of_missing_optional_options(tmp_path):
    '''缺少可选参数的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = testdevice
            localdirectory = /test/path
            checkinterval = 30

            [BaiduCloud]
            appname = 摄影素材自动备份
            appid = 47097507
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = 
            refreshtoken = 
            ''')
    yield temp_file  # 这将是你的测试配置文件
    # 测试完成后，文件会自动删除，无需手动清理

@pytest.fixture
def temp_config_file_of_more_useless_options(tmp_path):
    '''多了无用参数的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = testdevice
            localdirectory = /test/path
            checkinterval = 30
            more3 = c
                   
            [BaiduCloud]
            appname = 摄影素材自动备份
            appid = 47097507
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = 126.d4e31b6a2fb2281af4aa25ad6ee50999.YneUfftF6NPRxSiZZWRbLGhizfGyGV2S4lMuDyn.FeoBYA
            refreshtoken = 127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ
                   
            more2 = b
                   
            [MoreConfig]
            moreone = a
            ''')
    yield temp_file  # 这将是你的测试配置文件
    # 测试完成后，文件会自动删除，无需手动清理

@pytest.fixture
def temp_config_file_of_more_useful_options(tmp_path):
    '''多了有用参数的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = testdevice
            localdirectory = /test/path
            checkinterval = 30

            [BaiduCloud]
            appname = 摄影素材自动备份
            appid = 47097507
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = token1
            accesstoken = token2
            refreshtoken = 127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ
            ''')
    yield temp_file  # 这将是你的测试配置文件
    # 测试完成后，文件会自动删除，无需手动清理

@pytest.fixture
def temp_config_file_of_mess_up_options(tmp_path):
    '''正常的配置文件'''
    temp_file = tmp_path / "temp_config.ini"
    with open(temp_file, "w", encoding='utf-8') as file:
        file.write('''
            [LocalFiles]
            devicename = testdevice
            localdirectory = /test/path
            appname = 摄影素材自动备份
            appid = 47097507

            [BaiduCloud]
            checkinterval = 30
            appkey = H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb
            secretkey = pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6
            signkey = X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V
            accesstoken = 126.d4e31b6a2fb2281af4aa25ad6ee50999.YneUfftF6NPRxSiZZWRbLGhizfGyGV2S4lMuDyn.FeoBYA
            refreshtoken = 127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ
            ''')
    yield temp_file  


def test_load_config_with_normal_options(temp_config_file_of_normal_options):
    try:
        # 初始化 Config 对象
        config = Config(filename=str(temp_config_file_of_normal_options))
    except Exception as e:
        # 如果有任何异常抛出，则测试失败
        pytest.fail(f"初始化 Config 时抛出异常: {e}")

def test_load_config_with_missing_optional_options(temp_config_file_of_missing_optional_options):
    try:
        config = Config(filename=str(temp_config_file_of_missing_optional_options))
    except Exception as e:
        pytest.fail(f'缺少可选参数时初始化异常: {e}')

def test_load_config_with_missing_required_options(temp_config_file_of_missing_required_options):
    try:
        config = Config(str(temp_config_file_of_missing_required_options))
        pytest.fail(f'缺少必要参数时初始化竟然没有报错')

    except ValueError as e:
        if '是必需的' in str(e):
            assert True
        else:
            pytest.fail(f'缺少必要参数时初始化未能提出ValueError错误，而是{e}')

def test_load_config_with_more_useless_options(temp_config_file_of_more_useless_options):
    try:
        # 初始化 Config 对象
        config = Config(filename=str(temp_config_file_of_more_useless_options))
    except Exception as e:
        # 如果有任何异常抛出，则测试失败
        pytest.fail(f"配置文件有额外无关参数时初始化异常: {e}")

def test_load_config_with_more_useful_options(temp_config_file_of_more_useful_options):
    try:
        config = Config(str(temp_config_file_of_more_useful_options))
        pytest.fail("有重复配置时初始化异常")
    except:
        # 只要爆出异常就行
        assert True

def test_load_config_with_mess_up_options(temp_config_file_of_mess_up_options):
    try:
        config = Config(str(temp_config_file_of_mess_up_options))
        pytest.fail('打乱配置时初始化异常')
    except (ValueError):
        assert True

def test_load_config_with_no_file():
    '''没有配置文件时自动创建并抛出异常'''
    filename = 'tests/no_exsit.ini'
    try:
        config = Config(filename)
        pytest.fail('文件不存在时加载异常')
    except FileNotFoundError:
        if os.path.exists(filename):
            os.remove(filename)
            assert True
        else:
            pytest.fail(f'检测不到配置文件，生成默认配置时异常')

def test_get_local_config_with_normal(temp_config_file_of_normal_options):
    '''正常文件能读取'''
    config = Config(filename=str(temp_config_file_of_normal_options))

    # 调用 get_local_config 方法
    local_config = config.get_local_config()

    # 验证返回结果
    assert local_config['device_name'] == 'testdevice'
    assert local_config['local_directory'] == '/test/path'
    assert local_config['check_interval'] == 30

    # 调用 get_baidu_config 方法
    baidu_config = config.get_baidu_config()

    # 验证
    assert baidu_config['app_name'] == '摄影素材自动备份'
    assert baidu_config['app_id'] == '47097507'
    assert baidu_config['app_key'] == 'H794OU88Q5KXH89ahoPGVCFNMxVBb1Sb'
    assert baidu_config['secret_key'] == 'pWjzs8MIBw2fxutAXsxVpN0Pxa0OqRT6'
    assert baidu_config['sign_key'] == 'X3JHR8D=5g0!EP%RF1FzGDrMQFPQkn1V'
    assert baidu_config['access_token'] == '126.d4e31b6a2fb2281af4aa25ad6ee50999.YneUfftF6NPRxSiZZWRbLGhizfGyGV2S4lMuDyn.FeoBYA'
    assert baidu_config['refresh_token'] == '127.52f65085968dc5d433d3bcab00b86e87.Ym6GUUjm-GWFnY6-QbH0JeXeVUPwN0ov-UqgX88.JTRDBQ'

def test_update_and_save_normal_options(temp_config_file_of_normal_options):
    config = Config(temp_config_file_of_normal_options)
    update_options = {
        'accesstoken': 'update_token',
        'refreshtoken': 'update_refresh'
    }
    section = 'BaiduCloud'
    config.update_save(section, update_options)
    config2 = Config(temp_config_file_of_normal_options)

    localconfig1 = config.get_local_config()
    localconfig2 = config2.get_local_config()

    baiduconfig1 = config.get_baidu_config()
    baiduconfig2 = config2.get_baidu_config()

    assert localconfig1 == localconfig2
    assert baiduconfig1['app_name'] == baiduconfig2['app_name']
    assert baiduconfig1['app_id'] == baiduconfig2['app_id']
    assert baiduconfig1['app_key'] == baiduconfig2['app_key']
    assert baiduconfig1['secret_key'] == baiduconfig2['secret_key']

    assert baiduconfig2['access_token'] == 'update_token'
    assert baiduconfig2['refresh_token'] == 'update_refresh'

def test_update_and_save_no_exist_options():
    try:
        config = Config(temp_config_file_of_normal_options)
        update_options = {
            'accesstoken' : 'update_token',
            'noexist' : 'what?'
        }
        section = 'BaiduCloud'
        config.update_save(section, update_options)
        pytest.fail('更新不存在配置时未能提出异常')
    except:
        assert True

def test_update_and_save_wrong_sections_options():
    try:
        config = Config(temp_config_file_of_normal_options)
        update_options = {
            'accesstoken' : 'update_token',
            'refreshtoken' : 'update_refresh'
        }
        section = 'LocalFiles'
        config.update_save(section, update_options)
        pytest.fail('更新区块错误配置时未能提出异常')
    except:
        assert True
