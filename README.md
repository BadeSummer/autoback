# Autoback Tool

这个项目是一个Python程序，它的功能是监测本地指定文件夹中的新文件，并自动将它们上传到百度网盘。这个工具的初衷其实是为了解决大量文件的传输而设立的，每天`70+GB`的文件需要从远端传回本地NAS。综合考虑后的曲线救国方案：先上传到百度网盘，再从百度网盘下载。

## 功能

- **文件监控**: 实时监控指定本地文件夹，检测新文件。
- **自动上传**: 将检测到的新文件自动上传到百度网盘。
- **配置灵活**: 通过 `config.ini` 文件自定义设置。

## 开始使用

### 前置要求

确保你的系统中已经安装了`Python=[3.9, 3.10, 3.11]`环境。

### 安装

1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/BadeSummer/autoback.git
   cd autoback
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 测试
使用`pytest`进行测试，安装与测试
```bash
pip install pytest
pytest
```

### 配置

在项目根目录下创建修改 `config.ini` 文件，并按照`config.example.ini`格式配置：

- `devicename`: 客户端的名称，上传路径会使用设备名称作为根目录
- `localdirectory`: 你想监控的本地文件夹路径。
- `checkinterval`: 本地文件检查的周期，单位为（分钟）。
- `accesstoken`: 你的百度网盘API访问令牌。
- `refreshtoken`: 更新token所需的token。

关于`appname`, `appid`, `appkey`, `secretkey`, `signkey` 配置的说明: 这个是百度api调用时所需要的，意思是什么客户端在使用api。默认设置是我自己创建的一个应用，随时可以自行替换。百度应用创建流程[这里](https://pan.baidu.com/union/doc/Bl0eta7z8)

以百度网盘api上传为例，上传路径是：`/apps/appname/devicename/localdirectory`

### 运行

运行以下命令以启动程序：

```bash
python main.py
```

## 贡献

如果你想为这个项目贡献代码或建议，请随时提交 pull request 或开 issue。

## 许可

此项目根据MIT许可证授权 - 详情见 [LICENSE](LICENSE) 文件。

## 致谢

- 感谢所有对此项目做出贡献的开发者。
- 感谢百度网盘团队提供的API。
