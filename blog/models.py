from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息表
    """
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, unique=True)
    avatar = models.FileField(upload_to="avatars/", default="avatars/default.png", verbose_name="头像")
    create_time = models.DateTimeField(auto_now_add=True)
    blog = models.OneToOneField(to="Blog", to_field="nid", null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.username
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class Blog(models.Model):
    """
    博客信息
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)              # 个人博客标题
    site = models.CharField(max_length=32, unique=True)  # 个人博客后缀
    theme = models.CharField(max_length=32)              # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "blog站点"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    个人博客文章分类
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 分类标题
    blog = models.ForeignKey(to="Blog", to_field="nid",on_delete=models.CASCADE)  # 外键关联博客，一个博客站点可以有多个分类

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
    标签
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=32)  # 标签名
    blog = models.ForeignKey(to="Blog", to_field="nid",on_delete=models.CASCADE)  # 所属博客

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name="文章标题")  # 文章标题
    desc = models.CharField(max_length=255)                          # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)            # 创建时间

    # 评论数
    comment_count = models.IntegerField(verbose_name="评论数", default=0)
    # 点赞数
    up_count = models.IntegerField(verbose_name="点赞数", default=0)
    # 踩
    down_count = models.IntegerField(verbose_name="踩数", default=0)

    category = models.ForeignKey(to="Category", to_field="nid", null=True,on_delete=models.CASCADE)
    user = models.ForeignKey(to="UserInfo", to_field="nid",on_delete=models.CASCADE)
    tags = models.ManyToManyField(  # 中介模型
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),  # 注意顺序！！！
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name


class ArticleDetail(models.Model):
    """
    文章详情表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField()
    article = models.OneToOneField(to="Article", to_field="nid",on_delete=models.CASCADE)

    class Meta:
        verbose_name = "文章详情"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.article.title


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid",on_delete=models.CASCADE)
    tag = models.ForeignKey(to="Tag", to_field="nid",on_delete=models.CASCADE)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name = "文章-标签"
        verbose_name_plural = verbose_name
    def __str__(self):
        return "{}-{}".format(self.article.title,self.tag.title)


class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to="UserInfo", null=True,on_delete=models.CASCADE)
    article = models.ForeignKey(to="Article", null=True,on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = (("article", "user"),)  #联合唯一 一个用户只能对一篇文章进行某个赞操作
                                                  #不能出现 一个用户对一篇文章既点赞又点踩
        verbose_name = "文章点赞"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """
    评论表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article", to_field="nid",on_delete=models.CASCADE)
    user = models.ForeignKey(to="UserInfo", to_field="nid",on_delete=models.CASCADE)
    content = models.CharField(max_length=255)  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey("self", null=True, blank=True,on_delete=models.CASCADE)  # blank=True 在django admin里面可以不填

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
