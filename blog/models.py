# coding=utf-8
from __future__ import unicode_literals
from django.db import models
from django.core.urlresolvers import reverse
from collections import defaultdict

import datetime

'''
所有的model必须继承django.db.models
类Article即表示Blog的文章
一个类被django映射成数据库中对应的一个表,类名即表名
类的属性(field),比如下面的title,body等对应着数据库的表的属性列
'''


class ArticleManage(models.Manager):  # 继承自默认的manager，为其添加一个自定义的archive方法
    def archive(self):
        date_list = Article.objects.datetimes('create_time', 'month', order='DESC')
        # 获取到降序排列的精确到月份且已去重和文章发表时间列表
        # 并把列表转为一个字典，字典的键为年份，值为年份下对应的月份列表
        date_dict = defaultdict(list)
        for d in date_list:
            date_dict[d.year].append(d.month)
        # 模版并不支持defaultdict，因此我们把它转换成一个二级列表，由于字典转换后无序，所以重新降序排序
        return sorted(date_dict.items(), reverse=True)


class Article(models.Model):
    STATUS_CHOICES = (
        ('d', 'Draft'),
        ('p', 'Published'),
    )
    # 在status时说明
    objects = ArticleManage()

    title = models.CharField(u'标题', max_length=80)
    '''
    文章标题，CharField 表示对应数据库中表的列是用来存字符串的。
    '标题'是一个位置参数（verbose_name）。
    max_length 表示能存储的字符串的最大长度。
    '''

    body = models.TextField(u'正文')
    # 正文 TextField用来存储大文本字符

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    # 文章创建时间 DateTimeField用于存储时间，设定auto_now_add参数为真，则在文章被创建时会自动添加创建时间

    last_modified_time = models.DateTimeField(u'修改时间', auto_now=True)
    # 文章最后修改时间 auto_now=True表示每次修改文章时自动添加修改的时间

    status = models.CharField(u'文章状态', max_length=1, choices=STATUS_CHOICES)
    '''
    STATUS_CHOICES,field的choices参数需要的值，
    choices选项会使该field在被渲染成form时被渲染成一个select组件，
    这里有两个状态，一个为Draft（草稿），一个为Published（已发送）
    即select组件有两个选项：Draft and Publish。
    但是存储在数据库中的值分别为‘d’ and ‘p’，这就是choices的作用
    '''

    abstract = models.CharField(u'摘要', max_length=70, blank=True, null=True,
                                help_text=u'可选，若为空将摘取正文的前54个字符')
    # 文章摘要，help_text在该field被渲染成form时显示帮助信息

    views = models.PositiveIntegerField(u'浏览量', default=0)
    # 浏览量，PositiveIntegerFied存储类型为非负整数

    likes = models.PositiveIntegerField(u'点赞数', default=0)
    # 点赞数，同上

    topped = models.BooleanField(u'置顶', default=False)
    # 是否置顶，BooleanField存储布尔值，默认为False（否）

    category = models.ForeignKey('Category', verbose_name=u'分类',
                                 null=True,
                                 on_delete=models.SET_NULL)
    '''
    文章的分类，ForeignKey即数据库中的外键。外键的定义是：如果数据库中某个表的列的值是另外一个表的主键。
    外键定义了一个一对多的关系，这里即一篇文章对应一个分类，而一个分类下可能有多篇文章。
    on_delete=models.SET_NULL表示删除某个分类（category）后该分类下所有的Article的外键设为null（空）

    '''

    tags = models.ManyToManyField('Tag', verbose_name=u'标签集合', blank=True)

    def get_absolute_url(self):
        return reverse('blog: detail', kwargs={'article_id': self.pk})

    def __unicode__(self):        # 用于交互解释器显示表示该类的字符串
        return self.title

    class Meta:
        # Meta包含一系列选项，这里的ordering表示排序，-号表示逆序。即当从数据库中取出文章时，是按文章最后一次修改时间逆序排列的。
        ordering = ['-last_modified_time']


class Category(models.Model):       # 另一个表，存储文章的分类信息
    name = models.CharField(u'类名', max_length=20)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField(u'最后修改时间', auto_now=True)

    def __unicode__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(u'标签名', max_length=25)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    last_modified_time = models.DateTimeField(u'最后修改时间', auto_now=True)

    def __unicode__(self):
        return self.name


class BlogComment(models.Model):
    user_name = models.CharField(u'评论者名字', max_length=100)
    user_email = models.EmailField(u'评论者邮箱', max_length=255)
    body = models.TextField(u'评论内容')
    created_time = models.DateTimeField(u'评论发表时间', auto_now_add=True)
    article = models.ForeignKey('Article', verbose_name=u'评论所属文章', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.body[:20]
