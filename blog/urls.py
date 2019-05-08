# Author:Jesi
# Time : 2018/9/5 19:32
from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'up_down/',views.up_down),
    url(r'comment/', views.comment),
    url(r'comment_tree/(\d+)/', views.comment_tree),
    url(r'(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/',views.home),
    url(r'(?P<username>\w+)/$', views.home),  # 捕获到这个字段
    url(r'(\w+)/article/(\d+)$',views.article_detail), #文章详情articles_detail(request,jesi,1)
    # 后台管理url

]