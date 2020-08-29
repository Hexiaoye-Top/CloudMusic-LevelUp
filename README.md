# CloudMusic-LevelUp

> 网易云音乐刷歌升级脚本

## 脚本功能

1. PC端签到，并显示奖励的积分数值
2. 刷音乐播放量，每次限制最高500首，反复刷没什么用处

## 使用方式

### 安装依赖

```shell
pip install -r requirements.txt
```

### 执行脚本

脚本使用命令行参数输入变量

```shell
python action.py "手机号" "32位MD5密码加密值"
```

密码的MD5值计算可以在https://md5jiami.51240.com/上进行，取32位小写值

![](README/image-20200829112617823.png)

### 自定义歌单

鉴于网易云每天推荐的歌单不太够，就增加了自定义歌单的功能，也是使用参数的形式，支持多个歌单输入，例如：

```shell
python action.py "手机号" "32位MD5密码加密值" 5173689994 4901511925
```

由于限制500首，放多了也没有，并且每天网抑云只统计300首

## GitHub Actions部署

### 1.  Fork该仓库

### 2. 创建Secrets

创建PHONE，填入手机号

创建PASSWORD，填入32位MD5密码加密值

![](README/image-20200829120257532.png)

### 3. 启用Action

点击Actions，选择 **I understand my workflows, go ahead and enable them**

**每天0点会自动执行一次脚本**

![](README/image-20200829120815423.png)

![](README/image-20200829120847583.png)

## TODO:

这种刷歌的方式不太好，每次推荐的四个歌单似乎不到300首，以后有时间再改吧。