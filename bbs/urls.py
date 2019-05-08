"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog import views
from django.views.static import serve
from django.conf import settings
from blog import urls as blog_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^register/', views.register),

    # 将所有以blog开头的URL交给blog_urls处理
    url(r'^blog/', include(blog_urls)),

    # 主页
    url(r'^index/', views.index),

    # 极验滑动验证码 获取验证码的url
    url(r'^pc-geetest/register', views.get_geetest),

    # 专门用来校验用户名是否已被注册的接口
    url(r'^check_username_exist/$', views.check_username_exist),

    # 上传url
    url(r'^upload/', views.upload),


    url(r'^media/(?P<path>.*)$',serve,{"document_root":settings.MEDIA_ROOT}),
    url(r"backend/add_article/", views.add_article),
    url(r'^backend/$', views.cn_backend),
    # 删除
    url(r'^delete/$', views.delete),
    # 编辑
    url(r'^backend/edit_article/(?P<article_id>\w+)$', views.edit_article),

]
