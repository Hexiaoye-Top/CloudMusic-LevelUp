# CloudMusic-LevelUp

> 网易云音乐刷歌升级脚本，欢迎提 issue 和 requests 帮助增强脚本功能。
>
> [项目 GitHub 地址](https://github.com/Secriy/CloudMusic-LevelUp)

## 脚本功能

1. 登录网易云音乐
2. 执行签到，并显示奖励的积分数值
3. 刷音乐播放量，返回具体数值
4. 使用 GitHub Actions 部署脚本
5. 支持腾讯云函数部署脚本

## 使用方式

### 安装依赖

```shell
pip install -r requirements.txt
```

### 执行脚本

脚本使用命令行参数输入变量，其中手机号和密码为必填字段，其余均为可选字段。

```shell
# python action.py -h 查看usage
usage: action.py [-h] [-s SC_KEY] [-t TG_BOT_KEY TG_BOT_KEY] [-b BARK_KEY] [-w WECOM_KEY WECOM_KEY WECOM_KEY] [-p PUSH_PLUS_KEY] phone password

positional arguments:
  phone                 Your Phone Number.
  password              The plaint text or MD5 value of the password.

optional arguments:
  -h, --help            show this help message and exit
  -s SC_KEY             The SCKEY of the Server Chan.
  -t TG_BOT_KEY TG_BOT_KEY
                        The Token and Chat ID of your telegram bot.
  -b BARK_KEY           The key of your bark app.
  -w WECOM_KEY WECOM_KEY WECOM_KEY
                        Your Wecom ID, App-AgentID and App-Secrets.
  -p PUSH_PLUS_KEY      The token of your pushplus account.
```

手机号默认国际电话区号为中国大陆（+86），如果是海外用户请将手机号字段写为`区号+手机号`的格式，如`852+12343123`，国内用户无需此操作。

密码可以为明文或明文的 MD5 值，脚本会自动判断明文密码并进行 MD5 计算。

MD5 值计算可以在[MD5 在线加密](https://md5jiami.51240.com/)上进行，取 32 位小写值

![](README/image-20200829112617823.png)

示例：

```shell
python .\action.py 1xx014x4636 pass123456
```

```shell
python .\action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7
```

执行结果：

![image-20210428144956285](README/image-20210428144956285.png)

### 多账号

脚本支持多账号，在指定参数时按顺序以`,`（注意为英文逗号）分割多个账号和密码：

```shell
python .\action.py 1xx014x4636,2xx011x4226 1xxx2xx324x65fx6xb22846ea8xcx0x7,2xxx41x324x34fx6xb11546ea4xcx1x2
```

### 自定义歌单

鉴于有需要使用脚本指定歌单刷歌的需求，脚本增加了自定义歌单的功能，需要在*action.py*同级目录下新建纯文本文件*playlist.txt*，按行添加自定义的歌单即可，例如：

```
741934630
6614758882
2488376689
```

注意：当*playlist.txt*文件不为空时，脚本不会使用网易云音乐推荐的歌单刷听歌量，仅使用自定义的歌单。

### 消息推送

脚本提供了多种消息推送渠道供选择使用，便于用户查看执行结结果。以下多个推送方式可以同时多选使用。

#### Server 酱 Turbo 推送

使用 Server 酱 Turbo 版可以绑定微信，将脚本每次的运行结果推送到你的微信上。

使用方法：

1. 访问[Server 酱 Turbo 版官网](https://sct.ftqq.com/)，点击**登入**，使用微信扫码登录

2. 登入成功后，按照网站上的说明选择消息通道，如**方糖服务号**（于 2021 年 4 月停止服务）

3. 点击**SendKey**，找到自己的 SendKey，并复制

4. 执行脚本时带参数`-s`指定 SendKey

用例：

```shell
python action.py [手机号] [32位MD5密码加密值] -s [SendKey]
```

示例：

```shell
python action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7 -s SSS111111T111112f3e421
```

#### Telegram Bot 推送

使用 Telegram 机器人按时推送脚本执行结果。

使用方法：

1. 创建 Telegram 机器人并获取机器人 Token 以及个人账户的 Chat ID
2. 执行脚本时指定参数`-t`，其后输入 Token 和 Chat ID 两个参数，顺序固定

示例：

```shell
python action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7 -t 1172135555:AAAABBskKAAAeiE-BBacB1baODj1ccchcMc 1231315343
```

#### Bark 推送

使用 Bark App 实现推送（建议 iOS/iPadOS 用户使用）。

使用方法：

1. 安装 Bark 移动端程序
2. 复制应用内的示例 URL 并截取其中的 22 位随机字符串
3. 执行脚本时指定参数`-b`，后接上述 22 位字符串

示例：

```shell
python action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7 -b aaaaaaaaaaaaaaaaaaaaaa
```

#### pushplus 微信公众号推送

使用[pushplus](http://www.pushplus.plus/)平台进行推送。

使用方法：

1. 访问[pushplus](http://www.pushplus.plus/)官网，登录
2. 找到**一对一推送**，并复制你的**token**
3. 执行脚本时指定参数`-p`，后接上述 token 值

示例：

```shell
python action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7 -p aaa6aac77dc1111c2d22c2345555242e
```

#### 企业微信推送

使用方法:

1. 配置企业微信，获取企业 ID、应用 ID、应用 Secret
2. 执行脚本时指定参数`-w`，其后输入企业 ID、应用 ID 和应用 Secrets 三个参数，顺序固定

用例：

```shell
python action.py 1xx014x4636 1xxx2xx324x65fx6xb22846ea8xcx0x7 -w [企业ID] [应用ID] [应用Secrets]
```

## GitHub Actions 部署

### 1. Fork 该仓库

### 2. 创建 Secrets

- 创建 PHONE，填入手机号，多账号以`,`分割（必填）
- 创建 PASSWORD，填入 32 位 MD5 密码加密值，多账号以`,`分割（与 PASSWORD_PLAIN 字段二选一）
- 创建 PASSWORD_PLAIN，填入明文密码，多账号以`,`分割（与 PASSWORD 字段二选一）
- 创建 SC_KEY（Server 酱 SendKey，可选）
- 创建 TG_BOT_KEY（Telegram 机器人推送参数，以空格分割多个参数，可选）
- 创建 BARK_KEY（Bark 推送参数，可选）
- 创建 WECOM_KEY （企业微信推送参数，以空格分割多个参数，可选）
- 创建 PUSH_PLUS_KEY（pushplus 推送参数，可选）

![](README/image-20201110002853759.png)

### 3. 创建 playlist.txt（如无必要不要使用）

项目默认包含 playlist.txt 文件，填写内容即可，每行一个歌单号。

### 4. 启用 Action

点击 Actions，选择 **I understand my workflows, go ahead and enable them**

**由于 GitHub Actions 的限制，直接 fork 来的仓库不会自动执行！！！**

必须手动修改项目提交上去，最简单的方法就是修改下图的 README.md 文件（右侧有网页端编辑按钮）。

![image-20201022185210937](README/image-20201022185210937.png)

随便修改什么都行，修改完 commit 就可以了。

之后**每天 0 点**会自动执行一次脚本

![](README/image-20200829120815423.png)

![](README/image-20200829120847583.png)

### 4. 手动执行

GitHub 有手动执行的功能，点击下图 Run workflow 即可。

![](README/image-20201022192517489.png)

### 5. 多次执行（可选）

如果觉得每天刷的听歌量达不到要求，可以尝试每天多次执行的解决方案，修改 _.github/workflows/action.yml_ 内的 _cron_ 值为 **"0 4/16 \* \* \*"** ，即在每天的北京时间 0 点和 12 点执行。

## 腾讯云函数部署

具体步骤参考[腾讯云函数部署CloudMusic-LevelUp脚本](https://blog.secriy.com/2021/06/12/%E8%85%BE%E8%AE%AF%E4%BA%91%E5%87%BD%E6%95%B0%E9%83%A8%E7%BD%B2CloudMusic-LevelUp%E8%84%9A%E6%9C%AC/)

## 注意事项

- 脚本只支持 Python3 环境
- 手机号列表和密码列表信息必须按顺序一一对应
- 网易云音乐限制每天最多计算 300 首
- 必须手动修改内容，不然不会自动执行！
- 为了方便他人学习研究，脚本保留了网易云音乐完整的表单加密算法
- Server 酱的应用场景取决于个人，请跟据自己的需求选择消息通道并进行配置，如在使用和配置方面有疑问，可以提出 Issue 或直接联系 Server Chan 管理员

## TODO

- 脚本功能太少，今后考虑开发比较实用的新功能

## 联系方式

### 微信

![image](README/IMG_3483.png)
