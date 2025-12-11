from email.policy import default

from django.db import models

# Create your models here.
class BookList(models.Model):
    id=models.AutoField("id",primary_key=True)
    bookId=models.CharField('书籍编号',max_length=255,default='')
    tag=models.CharField('类型',max_length=255,default='')
    title=models.CharField('书名',max_length=255,default='')
    cover=models.CharField('封面',max_length=2555,default=0.0)
    author=models.CharField('作者',max_length=255,default=0)
    press=models.CharField('出版社',max_length=255,default='')
    year=models.CharField('出版年份',max_length=255,default='')
    pageNum = models.CharField('页码', max_length=255,default='')
    price = models.CharField('价格', max_length=255,default='')
    rate = models.CharField('评分', max_length=255,default='')
    starList = models.CharField('星级列表',max_length=255, default='')
    summary = models.TextField('描述', default='')
    detailLink = models.CharField('详情链接', max_length=255,default='')
    createTime = models.CharField('创建时间',max_length=2555,default='')
    comment_len = models.CharField('评论数量',max_length=255, default='')
    commentList = models.TextField('评论列表', default='')

    class Meta:
        db_table = 'booklist'

class User(models.Model):
    id= models.AutoField("id",primary_key=True)
    username = models.CharField("用户名", max_length=255, default='')
    password = models.CharField("密码", max_length=255, default='')
    createTime= models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = 'user'

# 新增用户行为记录模型
class UserBehavior(models.Model):
    id = models.AutoField("id", primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    book = models.ForeignKey(BookList, on_delete=models.CASCADE, verbose_name="图书")
    behavior_type = models.CharField("行为类型", max_length=20, choices=[
        ('view', '浏览'),
        ('rate', '评分'),
        ('favorite', '收藏'),
        ('click', '点击')
    ])
    rating = models.IntegerField("评分", default=0)  # 如果行为是评分，则记录评分值
    timestamp = models.DateTimeField("行为时间", auto_now_add=True)

    class Meta:
        db_table = 'user_behavior'
        verbose_name = "用户行为"
        verbose_name_plural = "用户行为"


