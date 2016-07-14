# coding:utf-8
from __future__ import unicode_literals
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView
from blog.models import Article, Category, Tag
import markdown2
from .models import BlogComment
from .forms import BlogCommentForm


class IndexView(ListView):

    # 首页视图，继承自ListView,用于展示从数据库中获取的文章列表

    template_name = "blog/index.html"
    # template_name属性用于指定使用哪个模版进行渲染

    context_object_name = "article_list"
    # context_object_name属性用于给上下文变量取名（在模版中使用该名字）

    def get_queryset(self):

        # 过滤数据，获取所有已发布的文章，并且将内容转成markdown形式

        article_list = Article.objects.filter(status='p')
        # 获取数据库中的所有已发布的文章，即filter(过滤)状态为'p'(已发布)的文章。
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
            # 将markdown标记的文本转为html文本
        return article_list

    def get_context_data(self, **kwargs):
        # 增加额外的数据，这里返回一个文章分类，以字典的形式
        kwargs['category_list'] = Category.objects.all().order_by('name')
        kwargs['date_archive'] = Article.objects.archive()
        # 调用archive方法，把获取到的时间列表插入到context上下文中以便在模版中渲染
        kwargs['tag_list'] = Tag.objects.all().order_by('name')  # tag_list加入context里
        return super(IndexView, self).get_context_data(**kwargs)


class ArticleDetailView(DetailView):
    # Django有基于类的视图DetailView，用于显示一个对象的详情页，继承即可用
    model = Article
    # 指定视图获取哪个model

    template_name = "blog/detail.html"
    # 指定要渲染的模版文件

    context_object_name = "article"
    # 在模版中需要使用的上下文名字

    pk_url_kwarg = 'article_id'
    # pk_url_kwarg用于接收一个来自url中的主键，然后根据这个主键进行查询
    # 在urlpatters中已经捕获这个article_id

    # 指定以上几个属性，已经能返回一个DetailView视图，为了让文章以markdown形式展现需重写get_object()方法
    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object()
        obj.body = markdown2.markdown(obj.body, extras=['fenced-code-blocks'], )
        return obj

    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = self.object.blogcomment_set.all()
        kwargs['form'] = BlogCommentForm()
        return super(ArticleDetailView, self).get_context_data(**kwargs)


class CategoryView(ListView):          # 继承子ListView，用于展示一个列表

    template_name = "blog/index.html"
    # 指定需要渲染的模版

    context_object_name = "article_list"
    # 指定模版中需要使用的上下文对象的名字

    def get_queryset(self):  #
        article_list = Article.objects.filter(category=self.kwargs['cate_id'], status='p')
        # 在url里捕获分类的id作为关键字参数（cate_id）传递给了CategoryView，传递的参数在kwargs属性中获取。

        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
        return article_list

    def get_context_data(self, **kwargs):    # 给视图曾加额外数据
        kwargs['category_list'] = (Category.objects.all().order_by('name'))
        # 增加一个category_list，用于在页面显示所有分类，按照名字排序
        return super(CategoryView, self).get_context_data(**kwargs)


class TagView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'article_list'

    def get_queryset(self):     # 根据指定的标签获取该标签下的全部文章
        article_list = Article.objects.filter(tags=self.kwargs['tag_id'], status='p')
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['tag_list'] = Tag.objects.all().order_by('name')
        return super(TagView, self).get_context_data(**kwargs)


class ArchiveView(ListView):
    template_name = "blog/index.html"
    context_object_name = "article_list"

    def get_queryset(self):     # 接收从url传递的year和month参数，转换成int类型
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        # 按照year和month过滤文章
        article_list = Article.objects.filter(create_time_year=year, create_time__month=month)
        for article in article_list:
            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['tag_list'] = Tag.objects.all.order_by('name')
        return super(ArchiveView, self).get_context_data(**kwargs)


class CommentPostView(FormView):
    form_class = BlogCommentForm
    template_name = 'blog/detail.html'

    def form_invalid(self, form):
        target_article = get_object_or_404(Article, pk=self.kwargs['article_id'])
        comment = form.save(commit=False)
        comment.article = target_article
        comment.save()
        self.success_url = target_article.get_absolute_url()
        return HttpResponseRedirect(self.success_url)

    def form_valid(self, form):
        target_article = get_object_or_404(Article, pk=self.kwargs['article_id'])
        return render(self.request, 'blog/detail.html', {
            'form': form,
            'article': target_article,
            'comment_list': target_article.blogcomment_set.all(),
        })
