# Author:Jesi
# Time : 2018/9/6 18:56
from django import template
from django.db.models import Count
from blog import models
register = template.Library()

@register.inclusion_tag("left_menu.html")
def get_left_menu(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog=user.blog

    #按日期归档
    # 利用SQL语句把格式化的时间取到，然后用任意一个数据字段统计一下有多少文章。把统计的数量和时间取到
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").order_by("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    #找到个人博客站点所对应的文章分类和文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")

    #查询文章标签及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count("article")).values("title", "c")

    return {
        "user":user,
        "archive_list":archive_list,
        "category_list":category_list,
        "tag_list":tag_list,
    }
