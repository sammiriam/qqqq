# coding=utf-8
from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^article/(?P<article_id>\d+)$', views.ArticleDetailView.as_view(), name='detail'),
    url(r'^category/(?P<cate_id>\d+)$', views.CategoryView.as_view(), name='category'),
    url(r'^tag/(?P<tag_id>\d+)$', views.TagView.as_view(), name='tag'),
    url(r'^archive/(?P<year>\d+)/(?P<month>\d+)$', views.ArchiveView.as_view(), name='archive'),
    url(r'^article/(?P<article_id>\d+)/comment/$', views.CommentPostView.as_view(), name='comment'),
]

# 使用(?P<>\d+)的形式捕获值给<>中得参数，
# 比如(?P<article_id>\d+)，当访问/blog/article/3时，
# 将会将3捕获给article_id,这个值会传到views.ArticleDetailView,
# 这样我们就可以判断展示哪个Article了