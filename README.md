# 爬虫项目模板

该项目是爬虫项目模板。

## 1、如何改造

建议按数据的生命周期来一步步改造：
1. 数据的采集、解析；
1. 数据的处理、存储；
1. 爬虫的监控、告警与部署；

### 1.1、数据的采集、解析

需要改造的脚本包括：
1. spider_project/settings_account.py：记录登录和验证码识别服务的账号密码
1. spider_project/utils/api.py：如何构造 get 请求和 post 请求
1. spider_project/utils/cookies.py：如何模拟登录以获取 cookies
1. spider_project/utils/captcha.py：如何解析验证码，以应对反爬虫
1. spider_project/spiders/spider.py：如何构造爬虫请求的逻辑链，即基于当前页面生成新的爬虫请求
1. spider_project/middlewares.py：HeaderMiddleware 设置请求头

### 1.2、数据的处理、存储

需要改造的脚本包括：
1. spider_project/settings_account.py：记录数据库的账号密码
1. spider_project/sql/：用一个个 SQL 脚本定义了库和表
1. spider_project/items.py：与 spider_project/sql/ 里的脚本一一对应
1. spider_project/utils/mysql.py：数据库初始化时需要默认插入的数据
1. spider_project/middlewares.py：IgnoreNoChangesRequestMiddleware 避免重复发起请求
1. spider_project/pipelines.py：DuplicatesPipeline 避免重复存储数据，CleanPipeline 数据清洗，MysqlPipeline 数据存储

### 1.3、爬虫的监控、告警与部署

需要改造的脚本包括：
1. spider_project/settings_account.py：记录邮箱的账号密码
1. spider_project/pipelines.py：MailPipeline 生成告警邮件的正文
1. scrapy.cfg：部署爬虫的相关配置

## 2、爬虫设置

在开始爬虫前，请设置如下内容，从而确保爬虫可以正确运行

### 2.1、settings 设置

创建 `spider_project/settings_account.py` 文件，内容如下：

```python
USERNAME = 'xxx'  # 网站登录账号
PASSWORD = 'xxx'  # 网站登录密码

API_USERNAME = 'xxx'  # 冰拓 API 账号
API_PASSWORD = 'xxx'  # 冰拓 API 密码

MYSQL_USER = 'xxx'  # MYSQL 账号
MYSQL_PASSWORD = 'xxx'  # MYSQL 密码
MYSQL_HOST = 'xxx'  # MYSQL HOST
MYSQL_PORT = 3306  # MYSQL 端口
MYSQL_DATABASE = 'xxx'  # MYSQL 数据库名

MAIL_HOST = 'smtp.163.com'  # 发送邮件的服务器
MAIL_PORT = 25  # 端口号
MAIL_USER = 'xxxx'  # 用户名
MAIL_PASS = 'xxxxx'  # 发送邮箱的授权码
MAIL_TO = 'xxxx,xxxx'  # 收件人（注意一定要发给自己，不然可能会被判定为垃圾邮件）
```

### 2.2、环境设置

安装爬虫项目需要的一些模块

```bash
pip install -r requirements.txt
```

### 2.3、Pyppeteer 设置

项目中使用 Pyppeteer 框架实现了无页面的模拟登录 teambition ，但是其背后还是使用 Chromium 浏览器驱动。

在第一次使用 Pyppeteer 时，Pyppeteer 会校验是否已经下载过 Chromium ，如果没有，则会执行自动下载并保存。

我们可以让代码自动执行下载程序（国内下载速度感人……），也可以手动下载（将环境设置与爬虫解耦，避免因为下载 Chromium 失败导致爬虫失败）。

步骤稍微有点多：
1. 安装 Pyppeteer ：终端执行 `pip install pyppeteer` 。
1. 确认要安装的 Chromium 版本以及安装路径(右侧代码里的 `linux` 按操作系统还可修改为 `mac`、`win32` 或 `win64`)：终端执行 `python -c "import pyppeteer.chromium_downloader;print(pyppeteer.chromium_downloader.chromiumExecutable.get('linux'))"`，获得目标版本以及安装路径。
1. 创建安装路径：终端执行 `mkdir -p xxxx` 递归创建目录，然后再运行 `cd xxxx` 进入目录（将 xxx 改成上面的路径）。
1. 下载指定版本的 Chromium ：国内可以通过[淘宝源](https://npm.taobao.org/mirrors/chromium-browser-snapshots/)下载，注意版本要跟上面一致。
1. 解压安装：将下载好的 zip 压缩包放在指定目录下，并解压 `unzip xxxx`
1. 检查：运行`pyppeteer-install` ，如果直接显示 `[W:pyppeteer.command] chromium is already installed.` 则代表成功；否则请检查上面的操作是否被正确地依次执行了。

另外，在 linux 服务器上安装 Pyppeteer 还要有其他操作（以 root 用户执行下面的语句）

1. 安装依赖库（解决 `BadStatusLine: GET /json/version HTTP/1.1` 报错）
```bash
yum install pango.x86_64 libXcomposite.x86_64 libXcursor.x86_64 libXdamage.x86_64 libXext.x86_64 libXi.x86_64 libXtst.x86_64 cups-libs.x86_64 libXScrnSaver.x86_64 libXrandr.x86_64 GConf2.x86_64 alsa-lib.x86_64 atk.x86_64 gtk3.x86_64 nss.x86_64 -y
```

2. 安装字体（解决中文字体显示的问题）
```bash
yum install ipa-gothic-fonts xorg-x11-fonts-100dpi xorg-x11-fonts-75dpi xorg-x11-utils xorg-x11-fonts-cyrillic xorg-x11-fonts-Type1 xorg-x11-fonts-misc -y
```

这里也记录一下 Ubuntu 需要的依赖：

```bash
sudo apt install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
```

### 2.4、初始化数据库

执行下面的代码，将会执行 `spider_project/sql` 下的所有建表 sql 脚本。

```bash
python init_db.py
```

## 3、运行爬虫

请先确保完成了上面的所有设置。

在 `spider_project/spiders` 的 `project.py` 脚本里，我已经定义了名为 `project` 的爬虫。

执行下面的代码，运行爬虫。

```bash
scrapy crawl project
```

期间会先模拟登录获取 cookies，然后异步地执行爬取、清洗、存储等动作。

结束后，检查数据库，看看数据是否成功写入~

## 4、部署

下面展示了爬虫部署的全流程。

实际上，3.1、3.4 和 3.5 这 3 个小节完全可以独立运行在远程服务器上。本地开发完爬虫后，再使用 Scrapyd-clint 将爬虫打包和发送到服务器上进行统一的管理。

但为了更好地介绍，现在将这些过程都放在一起。

### 4.1、服务端：启动 Scrapyd

首先，启动 Scrapyd 。

```bash
scrapyd
```

Scrapyd 其实就是一个服务端，可以允许我们通过 HTTP JSON 的方式来控制爬虫（之后运行就可以不通过命令行了）。

但现在 Scrapyd 服务里面没有任何爬虫项目，让我们先保持 Scrapyd 的运行状态。


### 4.2、客户端：部署爬虫

在项目根目录下，可以看到 `scrapy.cfg` 文件，用于项目打包的配置。

`[deploy]` 里：
* `url` ：默认是 `http://localhost:6800/` ，即默认 Scrapyd 是本地启动且使用了 6800 端口，这个可以根据实际 Scrapyd 部署的位置来修改（ Scrapyd 也可以部署在远程服务器上）。
* `project`：爬虫项目的名称
* `version`：本次部署的爬虫版本
* `username`：scrapyd 账号
* `password`：scrapyd 密码

现在，我们本地已经运行了 Scrapyd ，那么可以直接运行下面的代码：

```bash
scrapyd-deploy
```

这句代码其实是利用 scrapy-client (客户端)，将本地的 scrapy 项目打包后，发送到 Scrapyd 服务端 `http://localhost:6800/`。 

运行后，可以看到当前目录下多了 build、dbs、eggs、logs、project.egg-info 等文件夹。

此时，打开浏览器到 http://localhost:6800/ 观察 Scrpyd 的页面，如果看到页面上显示 `Available projects: spider_project, default`，则代表添加成功。

到这一步，只是上传了爬虫项目，但还未启动。

### 4.3、ScrapydWeb

ScrapydWeb 是基于 Scrapyd 的一个 Web 应用，真正地实现了通过鼠标操作爬虫的目标。

运行方式也很简单，运行后会在当前目录下生成 `scrapydweb_settings_vXXX.py` 配置文件。

```bash
scrapydweb
```

`scrapydweb_settings_vXXX.py` 配置文件里提供了许多可修改的配置，常用的有：
* SCRAPYDWEB_PORT：ScrapydWeb 启动时占用的端口，如 6801。
* ENABLE_AUTH、USERNAME 和 PASSWORD：是否开启了 HTTP 认证，以及对应的账号和密码。
* LOCAL_SCRAPYD_SERVER、LOCAL_SCRAPYD_LOGS_DIR、ENABLE_LOGPARSER：如果 scrapyd 和 scrapydweb 运行在同一台机器上，则需要正确地指定 scrapyd 服务地址、其日志文件路径以及将 ENABLE_LOGPARSER 设为 True

如果本地运行 scrapydweb ，且将 SCRAPYDWEB_PORT 设为 6801，就可以打开网页 http://localhost:6801/ ，输入之前设定的账号密码（若有），进入页面。 

一开始进来的时候，可能什么都没有，首先添加爬虫（点击左边栏的 `Run Spider`）。

然后，选择项目、版本、爬虫，依次点击`Check CMD` 和 `Run Spider`：

最后，可以看到爬虫任务的状态从 `Pending` 变为 `Running`，最后变成 `Finished`，查看日志检查爬虫运行情况。


### 4.4、持久化

无论是 Scrapyd 还是 ScrapydWeb ，都需要保持运行才可以持续地提供服务。

建议使用 supervisor 来管理服务。

将 scrapyd 和 scrapydweb 各自的 supervisor 配置文件放入指定路径下后，运行：

```bash
supervisorctl update
```

详细的解析，可从网上查阅资料。
