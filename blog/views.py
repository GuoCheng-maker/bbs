import threading
import os
import json
from django.db import transaction  # 事务操作
from django.contrib.auth.decorators import login_required  # 用户登录证装饰器
from django.db.models import Count, F
from django.core.mail import send_mail  # 发送邮件
from django.http import JsonResponse  # Json数据返回到前端
from django.utils.safestring import mark_safe
from util import logging  # log日志

from bs4 import BeautifulSoup
from bbs import settings
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib
from blog import forms, models
from util.page import Pagination

# 记录登录日志和操作日志
login_logger = logging.log_handle('login')
handle_logger = logging.log_handle('handle')


# Create your views here.

# 使用极验滑动验证码的登录
def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]

        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)  # 将登录用户赋值给 request.user
                ret["msg"] = "/index/"
                login_logger.info("[%s]登录成功" % user)
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
                login_logger.error("[%s]登录失败" % user)
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login.html")


# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 注册的视图函数
def register(request):
    if request.method == "POST":
        ret = {"status": 0, "msg": ""}
        form_obj = forms.RegForm(request.POST)
        # 帮我做校验
        if form_obj.is_valid():
            # 校验通过，去数据库创建一个新的用户
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            user = request.POST.get("username")
            if avatar_img is not None:
                with transaction.atomic():
                    models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_img)
                    blog_obj = models.Blog.objects.create(title="%s的博客" % user, site=user, theme="jesi.css")
                    models.Tag.objects.create(title="%s的生活" % user, blog=blog_obj)
                    models.Category.objects.create(title="%s的IT" % user, blog=blog_obj)
            else:
                with transaction.atomic():
                    models.UserInfo.objects.create_user(**form_obj.cleaned_data)
                    blog_obj = models.Blog.objects.create(title="%s的博客" % user, site=user, theme="jesi.css")
                    models.Tag.objects.create(title="%s的生活" % user, blog=blog_obj)
                    models.Category.objects.create(title="%s的IT" % user, blog=blog_obj)

            login_logger.info("[%s]注册成功" % user)
            ret["msg"] = "/login/"
            return JsonResponse(ret)
        else:
            ret["status"] = 1
            ret["msg"] = form_obj.errors
            return JsonResponse(ret)
    # 生成一个form对象
    form_obj = forms.RegForm()
    # print(form_obj.fields)
    return render(request, "register.html", {"form_obj": form_obj})


# 校验用户名是否已被注册
def check_username_exist(request):
    ret = {"status": 0, "msg": ""}
    username = request.GET.get("username")
    is_exist = models.UserInfo.objects.filter(username=username)
    if is_exist:
        ret["status"] = 1
        ret["msg"] = "用户名已被注册！"
    return JsonResponse(ret)


# 注销
def logout(request):
    login_logger.info("[%s]退出" % request.user.username)
    auth.logout(request)
    return redirect("/index/")


# 博客主页
def index(request):
    # 查询所有的文章列表
    article_list = models.Article.objects.all()
    # 查询所有的用户
    user_list = models.UserInfo.objects.filter(is_superuser=0).all()
    # 加入分页器
    data_count = article_list.count()
    current_page = int(request.GET.get("page", 1))
    base_path = request.path

    pagination = Pagination(current_page, data_count, base_path, request.GET, per_page_num=8, pager_count=11)
    # 将数据进行分页
    article_list = article_list[pagination.start:pagination.end]
    return render(request, "index.html",
                  {"article_list": article_list, "pagination": pagination, "user_list": user_list})


# 个人主页
def home(request, username, **kwargs):
    # print(username)
    handle_logger.info("[%s]进入[%s]的主页" % (request.user.username, username))
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    # 找到书籍内user对象为上面传入user的人的文章
    article_list = models.Article.objects.filter(user=user)
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "category":
            article_list = models.Article.objects.filter(user=user).filter(category__title=param)
        elif condition == "tag":
            article_list = models.Article.objects.filter(user=user).filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = models.Article.objects.filter(user=user).filter(create_time__year=year,
                                                                           create_time__month=month)
    # 查询当前站点的每一个分类名称以及对应的文章数
    cate_list = models.Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list(
        "title", "c")

    # 查询当前站点的每一个标签名称以及对应的文章数
    tag_list = models.Tag.objects.filter(blog=blog).values('pk').annotate(c=Count('article')).values_list('title', 'c')

    # 统计年月日
    date_list = models.Article.objects.filter(user=user).extra(
        select={'y_m_date': "date_format(create_time,'%%Y-%%m')"}).values('y_m_date').annotate(
        c=Count('nid')).values_list('y_m_date', 'c')

    ret_dic = {}
    ret_dic['username'] = username
    ret_dic['article_list'] = article_list
    ret_dic['blog'] = blog
    print(user,blog)
    ret_dic['tag_list'] = tag_list
    ret_dic['date_list'] = date_list
    ret_dic['cate_list'] = cate_list
    return render(request, "home.html", ret_dic)


# 文章详情页
def article_detail(request, username, pk):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=pk).first()
    comment_list = models.Comment.objects.filter(article_id=pk)
    handle_logger.info("[%s]正在查看[%s]的文章[%s]" % (request.user.username, username, article_obj.title))
    return render(request, "article_detail.html",
                  {
                      "username": username,
                      "blog": blog,
                      "article": article_obj,
                      "comment_list": comment_list,
                  }
                  )


# 点赞踩视图
def up_down(request):
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))
    user = request.user
    article_obj = models.Article.objects.filter(pk=article_id).first()
    response = {"status": True}
    try:
        models.ArticleUpDown.objects.create(user=user, article_id=article_id, is_up=is_up)
        if is_up:
            # 创建一条点赞记录
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
            handle_logger.info("[%s]推荐了[%s]文章" % (request.user.username, article_obj.title))
        else:
            # 创建一条踩的记录
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
            handle_logger.info("[%s]踩了下[%s]文章" % (request.user.username, article_obj.title))
    except Exception as e:
        response["status"] = False
        response["first_action"] = models.ArticleUpDown.objects.filter(user=user, article_id=article_id).first().is_up

    return JsonResponse(response)


# 评论相关
def comment(request):
    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    user_pk = request.user.pk
    content = request.POST.get("content")
    article_obj = models.Article.objects.filter(pk=article_id).first()
    response = {}
    if not pid:
        # 没有父评论
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content)
    else:
        # 有父评论
        comment_obj = models.Comment.objects.create(article_id=article_id, user_id=user_pk, content=content,
                                                    parent_comment_id=pid)

    # 文章评论数+1
    models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    handle_logger.info("[%s]评论了[%s]文章，评论内容是%s" % (request.user.username, article_obj.title, content))

    # 多进程发送邮件，这里我作为最高权限者是官方邮箱，往用户注册时的邮箱发信息。
    t = threading.Thread(target=send_mail, args=("你的文章【%s】新增了一条评论内容" % article_obj.title,
                                                 content,
                                                 settings.EMAIL_HOST_USER,
                                                 [request.user.email],
                                                 ))
    t.start()

    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d")
    response["content"] = comment_obj.content
    response["username"] = comment_obj.user.username

    return JsonResponse(response)


# 评论树
def comment_tree(request, article_id):
    ret = list(models.Comment.objects.filter(article_id=article_id).values("pk", "content", "parent_comment_id"))
    return JsonResponse(ret, safe=False)


# 后台管理
@login_required
def cn_backend(request):
    """后台管理页面"""
    login_logger.info("[%s]进入管理后台" % request.user.username)
    article_list = models.Article.objects.filter(user__username=request.user.username)
    return render(request, "backend.html", {"article_list": article_list})


# 添加文章
@login_required
def add_article(request):
    if request.method == "POST":
        title = request.POST.get("title")
        article_content = request.POST.get("article_content")

        user = request.user
        bs = BeautifulSoup(mark_safe(article_content), "html.parser")

        # 过滤非法标签,防止XSS攻击
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()

        desc = "摘要：" + str(bs.text)[0:50] + "..."
        article_obj = models.Article.objects.create(user=user, title=title, desc=desc)

        # 文章详情添加的是过滤后的soup文档树字符串
        models.ArticleDetail.objects.create(article=article_obj, content=str(bs))

        login_logger.info("【%s】添加了一篇文章%s" % (request.user.username, title))
        return redirect("/index/")
    return render(request, "add_article.html")


# 文章删除
def delete(request):
    """文章删除"""
    response = {"status": None}
    article_id = request.POST.get("article_id")
    article_obj = models.Article.objects.filter(pk=article_id).first()
    models.Article.objects.filter(nid=article_id).delete()
    response['status'] = 1

    login_logger.info("【%s】进入删除了一篇文章%s" % (request.user.username, article_obj.title))
    return JsonResponse(response)


# 文章编辑
@login_required

def edit_article(request, article_id):
    """编辑文章"""
    article_obj = models.Article.objects.filter(pk=article_id).first()
    origin_content = models.ArticleDetail.objects.filter(article_id=article_id).first()
    if request.method == "POST":
        title = request.POST.get("title")
        article_content = request.POST.get("article_content")

        user = request.user
        bs = BeautifulSoup(mark_safe(article_content), "html.parser")

        # 过滤非法标签,防止XSS攻击
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()

        desc = "摘要：" + str(bs.text)[0:50] + "..."
        models.Article.objects.filter(nid=article_id).update(user=user, title=title, desc=desc)
        new_article_obj = models.Article.objects.filter(pk=article_id).first()
        # 文章详情添加的是过滤后的soup文档树字符串
        print(new_article_obj,type(new_article_obj),article_id)
        models.ArticleDetail.objects.filter(article_id=article_id).update(article=new_article_obj,content=str(bs))
        login_logger.info("【%s】编辑了一篇文章%s" % (request.user.username, title))
        return redirect("/backend/")
    return render(request, "edit_article.html", {'article_obj': article_obj, "origin_content": origin_content})

# 上传文件
@login_required
def upload(request):
    img = request.FILES.get("upload_img")
    img_path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img.name)

    # 图片读取，写入服务端
    with open(img_path, "wb") as f:
        for line in img:
            f.write(line)

    # 文件预览功能
    res = {
        "error": 0,
        "url": "/media/add_article_img/" + img.name
    }
    return HttpResponse(json.dumps(res))
