# -*- coding: utf-8 -*-
#from tmitter.mvc import models
import time
from django.db import connection, models
from django.contrib import admin
from django.utils import timesince,html
from utils import formatter,function
from settings import *
import PIL,six
from StringIO import StringIO
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from ckeditor.fields import RichTextField

# category model
@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField('名称',max_length=20)
    
    def __unicode__(self):
        return self.name
    
    def save(self, **kwargs):
        self.name = self.name[0:20]
        return super(Category,self).save()        
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural ='分类'

    def __str__(self):
        return "%s | %s | %s" % (
            six.text_type(self.name))


# Area Model
class Area(models.Model):
    TYPE_CHOISES = (
        (0,'国家'),
        (1,'省'),
        (2,'市'),
        (3,'区县'),
    )
    name = models.CharField('地名',max_length=100)
    code = models.CharField('代码',max_length=255)
    type = models.IntegerField('类型',choices=TYPE_CHOISES)
    parent = models.IntegerField('父级编号(关联自已)')
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'所在地'
        verbose_name_plural =u'所在地'


SEX=(('0','男'),('1','女'),)
# User model
class User(models.Model):
    id = models.AutoField(primary_key = True)

    username = models.CharField('用户名',max_length = 20)
    password = models.CharField('密码',max_length = 100)    
    realname = models.CharField('姓名',max_length = 20,blank=True)
    email = models.EmailField('Email')
    face = models.ImageField('头像',upload_to='face/%Y/%m/%d',default='',blank=True)
    url = models.CharField('个人主页',max_length=200,default='',blank=True)
    about = models.TextField('关于我',max_length = 1000,default='',blank=True)
    addtime = models.DateTimeField('注册时间',auto_now = True)
    friend = models.ManyToManyField("self",verbose_name='朋友',blank=True)
    #新添加的
    sex=models.CharField('性别',max_length=1,choices=SEX,default='0',blank=True)
    friend_num=models.IntegerField('好友数',default=0)
    note_num=models.IntegerField('消息数',default=0)
    # 标签，分数 用于推荐用户
    grade=models.IntegerField('分数',default=60)
    sign=models.CharField('标签',max_length=200,default='',blank=True)
    #日志，操作记录
    logger=models.TextField(blank=True,verbose_name='日志',default='')
    
    def __unicode__(self):
        return self.username
    
    def addtime_format(self):
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')
       
    def save(self,modify_pwd=True):
        if modify_pwd:
            self.password = function.md5_encode(self.password)
        self.about = formatter.substr(self.about,20,True)
        super(User,self).save()
        
    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'


# 消息
class Note(models.Model):
    
    id = models.AutoField(
        primary_key = True
    )
    message = models.TextField('消息')
    addtime = models.DateTimeField('发布时间',auto_now = True)
    category = models.ForeignKey(Category,verbose_name='来源')
    user = models.ForeignKey(User,verbose_name='发布者')
    #新添加的
    poll_num=models.IntegerField(default=0,verbose_name='点赞数')
    comment_num=models.IntegerField(default=0,verbose_name='评论数')
    repeat_num=models.IntegerField(default=0,verbose_name='转发数')
    tread_num = models.IntegerField(default=0, verbose_name='踩数')
    browse_num=models.IntegerField(default=0,verbose_name='浏览数')


    # comment=models.ForeignKey(Comment,verbose_name='评论')
    
    def __unicode__(self):
        return self.message
    
    def message_short(self):                        # 缩略形式的消息
        return formatter.substr(self.message,30)

    def addtime_format_admin(self):         # 获取发布时间
        return self.addtime.strftime('%Y-%m-%d %H:%M:%S')
        
    def category_name(self):
        return self.category.name
    
    def user_name(self):
        return self.user.username

    def save(self):
        self.message = formatter.content_tiny_url(self.message)
        self.message = html.escape(self.message)
        self.message = formatter.substr(self.message,140)
        super(Note, self).save()
    
    class Meta:
        verbose_name = u'消息'
        verbose_name_plural = u'消息'
    
    def get_absolute_url(self):     # 获取详细的信息页面的URL
        return APP_DOMAIN + 'message/%s/' % self.id
    

#消息的评论
class Comment(models.Model):
    user=models.ForeignKey(User,verbose_name='评论者',null=True)
    note=models.ForeignKey(Note,verbose_name='评论消息',null=True,on_delete=models.CASCADE)
    comment_parent=models.ForeignKey('self',verbose_name='回复',null=True,blank=True)
    content=models.TextField(verbose_name='评论内容')
    poll_num=models.IntegerField(default=0,verbose_name='点赞数')
    tread_num=models.IntegerField(default=0,verbose_name='踩数')
    reply_num=models.IntegerField(default=0,verbose_name='回复数')
    pub_date=models.DateTimeField(auto_now_add=True,verbose_name='发表时间')
    up_date=models.DateTimeField(auto_now=True,verbose_name='更新时间')

    def __unicode__(self):
        #return '%s,%s,%d'%(self.user_name(),self.content,str(self.comment_parent_id()))
        return self.content

    def user_name(self):
        return self.user.username

    def comment_parent_id(self):
        return self.comment_parent.content

    def pub_time_format_admin(self):         # 获取发布时间
        return self.pub_date.strftime('%Y-%m-%d %H:%M:%S')

    class Meta:
        verbose_name = u'评论'
        verbose_name_plural = u'评论'

#点赞消息
class PollNote(models.Model):
    user=models.ForeignKey(User,null=True)
    note=models.ForeignKey(Note,null=True)
    ifpoll=models.BooleanField(default=False)

    def user_name(self):
        return self.user.username

    def note_content(self):
        return self.note.message

    class Meta:
        verbose_name = u'消息点赞'
        verbose_name_plural = u'消息点赞'

#踩消息
class ThreadNote(models.Model):
    user=models.ForeignKey(User,null=True)
    note=models.ForeignKey(Note,null=True)
    ifthread=models.BooleanField(default=False)

    def user_name(self):
        return self.user.username

    def note_content(self):
        return self.note.message

    class Meta:
        verbose_name = u'消息踩'
        verbose_name_plural = u'消息踩'

#踩评论
class TheadComment(models.Model):
    user=models.ForeignKey(User,null=True)
    comment=models.ForeignKey(Comment,null=True)
    note=models.ForeignKey(Note,null=True)
    ifthread=models.BooleanField(default=False)

    def user_name(self):
        return self.user.username

    class Meta:
        verbose_name = u'评论踩'
        verbose_name_plural = u'评论踩'

#点赞评论
class PollComment(models.Model):
    user=models.ForeignKey(User,null=True)
    comment=models.ForeignKey(Comment,null=True)
    note=models.ForeignKey(Note,null=True)
    ifpoll=models.BooleanField(default=False)

    def user_name(self):
        return self.user.username

    class Meta:
        verbose_name = u'评论踩'
        verbose_name_plural = u'评论踩'

#文章类型
class ArticleType(models.Model):
    name=models.CharField(max_length=30,verbose_name='类型')
    description=models.TextField(blank=True)
    create_date=models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name='文章类型'
        verbose_name_plural='文章类型'

    def __unicode__(self):
        return self.name


#文章
class Article(models.Model):

    title=models.CharField(max_length=30,verbose_name='标题')
    author=models.ForeignKey(User,verbose_name='作者')
    type=models.ForeignKey(ArticleType,verbose_name='类型')
    content=models.TextField("内容")
    privilege=models.BooleanField(default=False)  #默认不公开
    browse_num=models.IntegerField(default=0,verbose_name='浏览次数')
    repeat_num = models.IntegerField(default=0, verbose_name='转发数')
    like_num=models.IntegerField(default=0,verbose_name='喜欢次数')
    pub_date=models.DateTimeField(auto_now_add=True,verbose_name='发表日期')  #auto_now_add 不会更新时间
    update_date=models.DateTimeField(auto_now=True,verbose_name='更新时间')


    class Meta:
        ordering=['-update_date']
        verbose_name_plural='文章'

    def __unicode__(self):
        return self.title


#好友消息
class Message(models.Model):
    sender=models.ForeignKey(User,verbose_name='发送者',related_name='message_sender')
    receiver=models.ForeignKey(User,verbose_name='接受者',related_name='message_receiver')
    content=models.TextField()
    create_date=models.DateTimeField(auto_now_add=True,verbose_name='发送时间')
    update_date=models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:
        verbose_name_plural='好友消息'

#评论通知
class Notice(models.Model):
    sender=models.ForeignKey(User,verbose_name='发送者',related_name='notice_sender')
    receiver=models.ForeignKey(User,verbose_name='接受者',related_name='notice_receiver')
    comment=models.ForeignKey(Comment,verbose_name='评论内容',default=None,related_name='notice_comment')
    status=models.BooleanField(default=False,verbose_name='是否阅读')
    type=models.IntegerField('通知类型')  #  0：评论
    create_date=models.DateTimeField(auto_now_add=True,verbose_name='发送时间')
    update_date = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering=['-create_date']
        verbose_name_plural='通知'

    def __unicode__(self):
        return self.create_date_format_admin()                     #+'对你的消息进行了评论'

    def create_date_format_admin(self):         # 获取发布时间
        return self.create_date.strftime('%Y-%m-%d %H:%M:%S')

# 赞对方的消息
class Notice_poll(models.Model):
    sender = models.ForeignKey(User, verbose_name='发送者', related_name='notice_poll_sender')
    receiver = models.ForeignKey(User, verbose_name='接受者', related_name='notice_poll_receiver')
    pollNote = models.ForeignKey(PollNote, verbose_name='赞对方的消息', default=None)
    status = models.BooleanField(default=False, verbose_name='是否阅读')
    type = models.IntegerField('通知类型')  # 1
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        ordering = ['-create_date']
        verbose_name_plural = '通知'

    def __unicode__(self):
        return self.sender + '赞了你的消息'

# 踩对方的消息
class Notice_tread(models.Model):
    sender = models.ForeignKey(User, verbose_name='发送者', related_name='notice_tread_sender')
    receiver = models.ForeignKey(User, verbose_name='接受者', related_name='notice_tread_receiver')
    treadNote = models.ForeignKey(ThreadNote, verbose_name='踩对方的消息', default=None)
    status = models.BooleanField(default=False, verbose_name='是否阅读')
    type = models.IntegerField('通知类型')  # 2
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        ordering = ['-create_date']
        verbose_name_plural = '通知'

    def __unicode__(self):
        return self.sender + '踩了你的消息'

# 赞对方的评论
class Notice_like(models.Model):
    sender = models.ForeignKey(User, verbose_name='发送者', related_name='notice_like_sender')
    receiver = models.ForeignKey(User, verbose_name='接受者', related_name='notice_like_receiver')
    pollComment = models.ForeignKey(PollComment, verbose_name='赞对方的评论', default=None)
    status = models.BooleanField(default=False, verbose_name='是否阅读')
    type = models.IntegerField('通知类型')  # 3
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')

    class Meta:
        ordering = ['-create_date']
        verbose_name_plural = '通知'

    def __unicode__(self):
        return self.sender + '赞了你的评论'

#记录添加好友的消息
class Notice_friend(models.Model):
    sender=models.ForeignKey(User,verbose_name='发送者',related_name='notice_friend_sender')
    receiver=models.ForeignKey(User,verbose_name='接受者',related_name='notice_friend_receiver')
    status = models.BooleanField(default=False, verbose_name='是否阅读')
    type = models.IntegerField('通知类型')  # 4
    create_date=models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    class Meta:
        ordering=['-create_date']
        verbose_name_plural='添加好友通知'


#给对方评论
def comment_save(sender,instance,signal,*args,**kwargs):
    entity=instance
    if entity.user != entity.note.user:     #作者的回复不用通知作者
        if entity.comment_parent is None:   #评论不是回复给作者的也不用通知作者
            event=Notice(sender=entity.user,receiver=entity.note.user,type=0,comment=entity)
            event.save()
    if entity.comment_parent is not None:    #回复评论要给对方发送通知
        if entity.user.id != entity.comment_parent.user.id:   #自己给自己写评论不用通知
            event=Notice(sender=entity.user,receiver=entity.comment_parent.user,type=0,comment=entity)
            event.save()

# 赞对方的消息
def poll_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if entity.user.id != entity.note.user.id:
        event = Notice_poll(sender=entity.user, receiver=entity.note.user, type=1, pollNote=entity)
        event.save()

# 踩对方的消息
def tread_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if entity.user.id != entity.note.user.id:
        event = Notice_tread(sender=entity.user, receiver=entity.note.user, type=2, treadNote=entity)
        event.save()

# 赞对方的评论
def like_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if entity.user.id != entity.comment.user.id:
        event = Notice_like(sender=entity.user, receiver=entity.comment.user, type=3, pollComment=entity)
        event.save()


#消息相应函数注册
signals.post_save.connect(comment_save,sender=Comment)
signals.post_save.connect(poll_save,sender=PollNote)
signals.post_save.connect(tread_save,sender=ThreadNote)
signals.post_save.connect(like_save,sender=PollComment)










