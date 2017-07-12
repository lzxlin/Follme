# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import *
from django.conf.urls import  url, include
from django.contrib import admin
from mvc.feed import RSSRecentNotes,RSSUserRecentNotes
import django
import mvc.views
import django.contrib.syndication.views
import django.views.static
import django.conf.urls
import django.conf.urls.i18n
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

rss_feeds = {
    'recent': RSSRecentNotes,
}

rss_user_feeds = {
    'recent': RSSUserRecentNotes,
}

urlpatterns = [
    # Example:
    # (r'^note/', include('note.foo.urls')),
    url(r'^$',mvc.views.index),
    url(r'^p/(?P<_page_index>\d+)/$',mvc.views.index_page,name="tmitter-mvc-views-index_page"),
    url(r'^user/$',mvc.views.index_user_self,name='tmitter-mvc-views-index_user_self'),    #我的主页
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/$',mvc.views.index_user, name= "tmitter-mvc-views-index_user"),
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/(?P<_page_index>\d+)/$',mvc.views.index_user_page,name="tmitter-mvc-views-index_user_page"),
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/notice/comment/$',mvc.views.notice_comment_list,name='notice_comment_list'), #查看未读的评论
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/notice/poll/$',mvc.views.notice_poll_list,name='notice_poll_list'), #查看未读的赞
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/notice/tread/$',mvc.views.notice_tread_list,name='notice_tread_list'), #查看未读的踩
    url(r'^user/(?P<_username>[a-zA-Z\-_\d]+)/notice/like/$',mvc.views.notice_like_list,name='notice_like_list'),
    url(r'^users/$',mvc.views.users_index),   #查看所有的好友
    url(r'^users/(?P<_page_index>\d+)/$',mvc.views.users_list,name="tmitter-mvc-views-users_list"),
    url(r'^search/$', mvc.views.search,name='search'),  # 模糊匹配查找好友
    url(r'^search/(?P<_page_index>\d+)/$', mvc.views.search_index, name="tmitter-mvc-views-search_index"),
    url(r'myfriends/$',mvc.views.myfriends,name='myfriends'),    #我的好友列表
    url(r'^myfriends/(?P<_page_index>\d+)/$', mvc.views.myfriends_index, name="tmitter-mvc-views-myfriends_index"),
    url(r'^signin/$',mvc.views.signin),     #登录
    url(r'^signout/$',mvc.views.signout),   #退出登录
    url(r'^signup/$',mvc.views.signup),     #注册
    url(r'^settings/$',mvc.views.settings, name ='tmitter_mvc_views_settings'),    #头像上传
    url(r'^message/(?P<_id>\d+)/$',mvc.views.detail, name = "tmitter-mvc-views-detail"),    #展开消息内容
    url(r'^message/(?P<_note_id>\d+)/(?P<_page_index>\d+)/$',mvc.views.comment_page,name='comment_page'),  #跳转评论的页数
    url(r'^message/(?P<_id>\d+)/delete/$',mvc.views.detail_delete, name = "tmitter-mvc-views-detail_delete"),   #删除消息
    url(r'^message/(?P<_id>\d+)/delete2/$',mvc.views.detail_delete2, name = "tmitter-mvc-views-detail_delete2"),   #删除消息
    url(r'^message/(?P<_id>\d+)/poll/$',mvc.views.poll_note,name="poll_note"),    #点赞消息
    url(r'^message/(?P<_id>\d+)/tread/$',mvc.views.tread_note,name='tread_note'),  #踩消息
    url(r'^comment/(?P<_id>\d+)/like/$',mvc.views.like_comment,name='like_comment'),  #点赞评论
    url(r'^comment/(?P<_id>\d+)/reply/$',mvc.views.comment_reply,name='comment_reply'),  #回复评论
    url(r'^comment/(?P<_id>\d+)/(?P<_page_index>\d+)/delete/$',mvc.views.comment_delete,name='tmitter-mvc-views-comment_delete'),      #删除评论
    url(r'^friend/add/(?P<_username>[a-zA-Z\-_\d]+)/$',mvc.views.friend_add, name="tmitter-mvc-views-friend_add"),
    url(r'^friend/remove/(?P<_username>[a-zA-Z\-_\d]+)/$',mvc.views.friend_remove,name="tmitter-mvc-views-friend_remove"),
    url(r'^api/note/add/',mvc.views.api_note_add),
    # Uncomment this for admin:
    #url(r'^admin/(.*)',admin.site.urls),
    url(r'^admin/',admin.site.urls),
    url(r'^feed/rss/(?P<url>.*)/$', django.contrib.syndication.views.Feed, {'feed_dict': rss_feeds}),
    url(r'^user/feed/rss/(?P<url>.*)/$', django.contrib.syndication.views.Feed, {'feed_dict': rss_user_feeds}),	
#    url(r'^statics/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^i18n/', django.conf.urls.i18n.i18n_patterns),
    url(r'^home/$',mvc.views.test_ajax),
    url(r'^load_more_data/(?P<type>\d+)/',mvc.views.load_more_data,name='load_more_data'),  #加载更多的数据
    url(r'^range/$',mvc.views.rp_range,name='rp_range'),    #rp榜
    url('^recommend/$',mvc.views.recommend,name='recommend'),   #根据标签推荐好友

]+static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

