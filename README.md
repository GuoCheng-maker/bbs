# 个人Blog博客系统

>基于"python3.6.5"和"Django2.1"开发的的个人博客系统。

## 层级结构
    cd bbs; 
    tree .

```
├── bbs
│   ├── __init__.py
│   ├── settings.py              # 配置文件
│   ├── urls.py                  # 路由配置
│   └── wsgi.py                  # web网关模块
├── blog
│   ├── admin.py                 # 后台管理
│   ├── apps.py                  # 应用
│   ├── forms.py                 # form组件
│   ├── __init__.py
│   ├── migrations               # ORM生成文件
│   │   ├── 0001_initial.py
│   │   ├── __init__.py
│   ├── models.py                # 数据库模型表
│   ├── templatetags             # tag归档模块
│   │   ├── __init__.py
│   │   ├── my_tags.py
│   ├── tests.py
│   ├── urls.py                  # 二层分级路由
│   └── views.py                 # 视图函数
├── manage.py                    # 启动文件
├── media                        # 媒体文件相关
│   ├── add_article_img
│   └── avatars
├── static                       # 静态文件
│   ├── bootstrap
│   ├── fontawesome
│   ├── img
│   ├── jquery-3.3.1.js
│   ├── kindeditor
│   ├── mystyle.css
│   ├── setupajax.js
│   └── theme
│       ├── cyy.css
│       └── jesi.css
├── templates                    # 模板文件
│   ├── add_article.html
│   ├── article_detail.html
│   ├── base.html
│   ├── home.html
│   ├── index.html
│   ├── left_menu.html
│   ├── login.html
│   └── register.html
└── util                         # 工具包
    ├── __init__.py
    ├── page.py
```


## 主要功能：
- 用户的登录，注册，注销，使用滑动验证的人性化体验，并且对新注册用户，用户名重复进行了实时校验。
- 对邮箱格式，重复，以及密码长度有着更为细致的安全体验。
- 文章，页面，分类目录，标签的添加，删除，编辑等。
- 文章删除做了更加人性化的二次确认优化。
- 添加文章页面支持`编辑器`,支持代码高亮，支持图片图文和地址等各种格式的插入。
- 楼层回复功能，支持@用户的楼中楼回复。
- 侧边栏功能，时间归档，文章分类，文章标签等。
- 支持预防XSS攻击功能，防止恶意用户进行XSS代码攻击。
- 支持点赞点踩功能，并且进行了人性化的设置。

## 安装
使用pip安装：

 `pip install virtualenv`
 
 `virtualenv -p /usr/bin/python3.6 my_project_env`

 `source my_project_env/bin/activate`

 `pip3 install -Ur requirements/base.txt`


### 配置
配置都是在`setting.py`中.部分配置迁移到了后台配置中。

很多`setting`配置我都是写在环境变量里面的.并没有提交到`github`中来.例如邮件部分的配置等.你可以直接修改代码成你自己的,或者在环境变量里面加入对应的配置就可以了.

`test`目录中的文件都是为了`travis`自动化测试使用的.不用去关注.或者直接使用.这样就可以集成`travis`自动化测试了.

在`linux`环境中使用`Nginx`+`UWSGI`+`virtualenv`+`supervisor`来部署的脚本和`Nginx`配置文件.可以参考我的文章:

>[使用云服务器部署个人博客系统](https://www.cnblogs.com/geogre123/p/9791002.html)

有详细的部署介绍.


## 运行

 修改`blog/setting.py` 文件更新个人数据库配置，如下所示：

     DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'bbs',
            'USER': 'root',
            'PASSWORD': 'password',
            'HOST': 'host',
            'PORT': 3306,
        }
    }

### 创建数据库
mysql数据库中执行:
```sql
CREATE DATABASE `bbs`;
```
 然后终端下执行:

    python manage.py makemigrations
    python manage.py migrate
即可利用Django自带的ORM创建所需的MySQL库表。
### 创建超级用户

 终端下执行:
    
    `python manage.py createsuperuser`
    输入用户名以及相关密码后即可完成创建超级用户，登录admin.
    
    
### 开始运行：
 最后执行：
 `python manage.py runserver`


 浏览器打开: http://127.0.0.1:8000/  就可以看到效果了。
 
## 更多配置:
[更多配置介绍](https://www.cnblogs.com/geogre123/articles/10245221.html)

## 问题相关

有任何问题欢迎提Issue,或者将问题描述发送至我邮箱 `guocheng6868@126.com`.我会尽快解答.
