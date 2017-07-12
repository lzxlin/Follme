# -*- coding: utf-8 -*-
from django.http import HttpResponse,Http404, HttpResponseRedirect, HttpResponseServerError
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core import serializers
from django.utils.translation import ugettext as _
from settings import *
from mvc.models import *
from mvc.feed import RSSRecentNotes,RSSUserRecentNotes
from utils import mailer,formatter,function,uploader
import markdown2
from django.core.cache import cache
from django.utils.timezone import now,timedelta
from django.core.mail import send_mail
import collections
import json

# #################
# common functions
# #################

# do login
def __do_login(request,_username,_password):
    _state = __check_login(_username,_password)
    if _state['success']:
         # save login info to session
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['username'] = _username
        request.session['realname'] = _state['realname']
    
    return _state

# get session user id
def __user_id(request):
    return request.session.get('userid',-1)

# get sessio realname
def __user_name(request):
    return request.session.get('username','')

# return user login status
def __is_login(request):
     return request.session.get('islogin', False)
    
# check username and password
def __check_login(_username,_password):
    _state = {
        'success' : True,
        'message' : 'none',
        'userid' : -1,
        'realname' : '',
        'login_user':None,
    }
    try:
        _user = User.objects.get(username = _username)
        if(_user.password == function.md5_encode(_password)):
            _state['success']  = True
            _state['userid'] = _user.id
            _state['realname'] = _user.realname
            _state['login_user']=_user
        else:

            _state['success']  = False
            _state['message'] = '密码不正确'
    except (User.DoesNotExist):
        _state['success'] = False
        _state['message'] = '用户不存在'
    return _state

# check user was existed
def __check_username_exist(_username):
    _exist = True
    
    try:
        _user = User.objects.get(username = _username)
        _exist = True
    except (User.DoesNotExist):
        _exist = False

    return _exist

# post signup data
def __do_signup(request,_userinfo):

    _state = {
            'success' : False,
            'message' : '',
        }

    # check username exist
    if(_userinfo['username'] == ''):
        _state['success'] = False
        _state['message'] = '用户名不能为空'
        return _state

    if(_userinfo['password'] == ''):
        _state['success'] = False
        _state['message'] = '密码不能为空'
        return _state

    if (_userinfo['confirm'] == ''):
        _state['success'] = False
        _state['message'] = '确认密码不能为空'
        return _state

    if(_userinfo['realname'] == ''):
        _state['success'] = False
        _state['message'] = '真实姓名不能为空'
        return _state

    if(_userinfo['email'] == ''):
        _state['success'] = False
        _state['message'] = '电子邮箱不能为空'
        return _state
    
    # check username exist
    if(__check_username_exist(_userinfo['username'])):
        _state['success'] = False
        _state['message'] = '用户名已存在'
        return _state    

    # check password & confirm password
    if(_userinfo['password'] != _userinfo['confirm']):
        _state['success'] = False
        _state['message'] = '两次密码输入不一致'
        return _state

    _user = User(
                     username = _userinfo['username'],
                     realname = _userinfo['realname'] , 
                     password = _userinfo['password'],
                     email = _userinfo['email'],
                 )
    #try:
    _user.save()
    _state['success'] = True
    _state['message'] = '注册成功'
    #except:
        #_state['success'] = False
        #_state['message'] = '程序异常,注册失败.'
    
    # send regist success mail
    #mailer.send_regist_success_mail(_userinfo)

    return _state
    

# response result message page
def __result_message(request,_title=_('Message'),_message='未知错误，程序异常中断',_go_back_url='',_state={'',}):

    _islogin = __is_login(request)

    _user_id = __user_id(request)
    _user = User.objects.get(id=_user_id)
    _friends = _user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]

    notice_comment = Notice.objects.filter(receiver=_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_user, status=False).count()
        
    if _go_back_url == '':
        _go_back_url = function.get_referer_url(request)   #返回上一页
    
    # body content
    _template = loader.get_template('result_message.html')

    logger = []
    if _user:
        logger = list(reversed(_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    
    _context = Context({
        'page_title' : _title,
        'message' : _message,
        'go_back_url' : _go_back_url,
        'islogin' : _islogin,
        'state':_state,
        'user':_user,
        'login_user':_user,
        'friends':_friends,
        'notice_comment':notice_comment,
        'notice_poll':notice_poll,
        'notice_tread':notice_tread,
        'notice_like':notice_like,
        'logger': logger,
        'online_num': online_num,  # 在线人数
        'user_num': user_num,
        'lastday_num': lastday_num,
        'today_num': today_num,
    })
    
    _output = _template.render(_context)
    
    return HttpResponse(_output)
    

# #################
# view method
# #################

# home view
def index(request):
    '''
    返回首页，如果用户已经登录则返回用户和朋友的信息
    '''
    # return index_user(request,'')
    _user_name = __user_name(request)
    return index_user(request,'')        #return index_user(request,_user_name)

# user messages view by self
def index_user_self(request):
    _user_name = __user_name(request)
    return index_user(request,_user_name)

# user messages view
def index_user(request,_username):
    return index_user_page(request,_username,1)

# index page
def index_page(request,_page_index):
    return index_user_page(request,'',_page_index)

# 消息发布/浏览
def index_user_page(request,_username,_page_index):
    # get user login status
    _islogin = __is_login(request)
    _page_title = _('Home')
    
    try:
        # 更新post中的参数
        _message = request.POST['message']        
        _is_post = True
    except (KeyError):
        _is_post = False
    
    #保存信息
    if _is_post:                    #只有用POST方式访问时才保存消息
        # 检查是否登录
        if not _islogin:           #只有已经登录才能保存消息
            return HttpResponseRedirect('/signin/')
        
        #保存信息
        (_category,_is_added_cate) = Category.objects.get_or_create(name=u'网页')

        try:
            _user = User.objects.get(id = __user_id(request))    #获取当前登录的用户
        except:
            return HttpResponseRedirect('/signin/')
        #初始化模型化类Note实例，并保存
        _note = Note(message = _message,category = _category , user = _user)
        _note.save()
        _user.note_num+=1   #用户消息数加1
        _user.save()
        
        return HttpResponseRedirect('/') #重定向回主页面  return HttpResponseRedirect('/user/' + _user.username)

    # 获取朋友信息列表，不是POST方式访问
    _userid = -1
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE    #  每一页的起始信息
    _last_item_index = PAGE_SIZE * int(_page_index)      #   每一页的末尾信息

    _login_user_friend_list = None
    notice_comment=0
    notice_poll=0
    notice_tread=0
    notice_like=0
    notice_poll_like=0

    if _islogin:                                               # 好友列表
         # 如果用户登录则获取朋友信息
        _login_user = User.objects.get(username = __user_name(request))
        _login_user_friend_list = _login_user.friend.all()     #获取登录用户的朋友列表
        #获取未读消息
        notice_comment=Notice.objects.filter(receiver=_login_user,status=False).count()
        notice_poll=Notice_poll.objects.filter(receiver=_login_user,status=False).count()
        notice_tread=Notice_tread.objects.filter(receiver=_login_user,status=False).count()
        notice_like=Notice_like.objects.filter(receiver=_login_user,status=False).count()
        notice_poll_like=notice_like+notice_poll

    else:
        _login_user = None
    
    _friends = None    
    _self_home = False
    if _username != '':                             # 只获取某个用户的消息
        # there is get user's messages
        _user = get_object_or_404(User,username=_username)
        _userid = _user.id
        _notes = Note.objects.filter(user = _user).order_by('-addtime')
        _page_title = u'%s' % _user.username
        # get friend list
        #_friends = _user.friend.get_query_set().order_by("id")[0:FRIEND_LIST_MAX]
        _friends = _user.friend.order_by("id")[0:FRIEND_LIST_MAX]
        # print "................", _friends
        if(_userid == __user_id(request)):
            _self_home = True         
            
    else:                                               # 获取所有用户的消息
        _user = _login_user
        
        if _islogin:           # 展示用户和朋友的信息
            if _login_user.id==__user_id(request):
                _self_home=True
            _query_users = [_login_user]
            _query_users.extend(_login_user.friend.all())      #  展示用户
            _notes = Note.objects.filter(user__in = _query_users).order_by('-addtime')     # 展示用户消息
            for _n in _notes:
                _n.repeat_num=get_note_scancount(request,_n.id)   #获取浏览数
                _n.save()

            _friends=_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]
        else:                            #如果没有登录，则不允许查询
            _notes = []# Note.objects.order_by('-addtime')

    # page bar
    _page_bar = formatter.pagebar(_notes,_page_index,_username)
    
    # get current page
    _notes = _notes[_offset_index:_last_item_index]

    #zip(_notes,_messages)

    # body content
    _template = loader.get_template('index.html')

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info=get_info()
    online_num=system_info['loginUser']
    user_num=system_info['user_num']
    lastday_num=system_info['lastday_num']
    today_num=system_info['today_num']


    _context = {
        'page_title' : _page_title,   #页面
        'notes' : _notes,      #消息
        'islogin' : _islogin,    #是否登录
        'userid' : __user_id(request),     #登录人的id
        'self_home' : _self_home,
        'user' : _user,
        'page_bar' : _page_bar,
        'friends' : _friends,
        'login_user_friend_list' : _login_user_friend_list,
        'login_user':_login_user,
        'notice_comment':notice_comment,           #未阅读的消息
        'notice_poll':notice_poll,
        'notice_tread':notice_tread,
        'notice_like':notice_like,
        'notice_poll_like':notice_poll_like,
        'logger': logger,
        'online_num':online_num,    #在线人数
        'user_num':user_num,
        'lastday_num':lastday_num,
        'today_num':today_num,
        }
    
    _output = _template.render(_context)
    
    return HttpResponse(_output)


#删除消息（在首页或者主页的时候删除）
def detail_delete(request,_id):
    # get user login status
    _islogin = __is_login(request)    

    _note = get_object_or_404(Note,id=_id)
   
    _message = ""
    
    try:
        _note.user.note_num-=1    #消息数减1
        _note.user.save()
        _note.delete()
        _message = '消息删除成功'
    except:
        _message = '消息删除失败'
    
    return __result_message(request,_('Message %s') % _id,_message)

#删除消息2（在进入消息页面的时候删除）/message/(\d+)
def detail_delete2(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    _message = ""

    try:
        _note.user.note_num-=1
        _note.user.save()
        _note.delete()
        _message = '消息删除成功'
    except:
        _message = '消息删除失败'

    return __result_message(request, _('Message %s') % _id, _message,_go_back_url='/')

#删除评论
def comment_delete(request,_id,_page_index=1):

    _comment=get_object_or_404(Comment,id=_id)
    _note=_comment.note
    _message=''
    try:
        _comment.delete()
        _note.comment_num-=1      #更新评论数
        _note.save()
        _message='评论删除成功'
        return HttpResponseRedirect('/message/'+str(_note.id))
        #return comment_page(request, _note.id,_page_index)  # 删除成功，返回删除时的页面
    except:
       _message='评论删除失败'
    return __result_message(request,'Comment %s'%_id,_message)


# 登录
def signin(request):
    
    # get user login status
    _islogin = __is_login(request)
    _username=None
    _password=None
    _title = ''
    _message =''
    _login_user = ''
   
    try:
        # get post params
        _username = request.POST['username']
        _password = request.POST['password']
        _is_post = True
    except (KeyError):
        _is_post = False
    
    # check username and password
    if _is_post:
        _state = __do_login(request,_username,_password)

        if _state['success']:
            _title='登录成功'
            _message='恭喜你成功登录，快去发布自己的心情吧......'
            _login_user = User.objects.get(username=__user_name(request))
            # return __result_message(request,'登录成功','你已经登录',_state)
    else:
        _state = {
            'success' : False,
            'message' :'请先登录'
        }
    # body content
    _template = loader.get_template('result_message.html')

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    _context = {
        'page_title' :_title,
        'state' : _state,
        'go_back_url':'/',
        'islogn':_islogin,
        'login_user':_login_user,
        'message':_message,
        'logger':logger,
        'online_num': online_num,  # 在线人数
        'user_num': user_num,
        'lastday_num': lastday_num,
        'today_num': today_num,
        }
    _output = _template.render(_context)
    return HttpResponse(_output)


#注册
def signup(request):
    # check is login
    _islogin = __is_login(request)

    if(_islogin):
        return HttpResponseRedirect('/')

    _userinfo = {
            'username' : '',
            'password' : '',
            'confirm' : '',
            'realname' : '',
            'email' : '',
        }
    
    try:
        # get post params
        _userinfo = {
            'username' : request.POST['username'],
            'password' : request.POST['password'],
            'confirm' : request.POST['confirm'],
            'realname' : request.POST['realname'],
            'email' : request.POST['email'],
        }
        _is_post = True
    except (KeyError):        
        _is_post = False

    if(_is_post):
        _state = __do_signup(request,_userinfo)
    else:
        _state = {
            'success' : False,
            'message' :'注册'
        }

    _message='恭喜你的账号注册成功,快去登录吧！'
    
    if(_state['success']):    #成功时，尝试发邮箱

        _template = loader.get_template('result_message.html')
        _context = {
            'page_title': '注册成功',
            'go_back_url': '/',
            'message': _message,
        }
        _output = _template.render(_context)
        return HttpResponse(_output)
        #eturn __result_message(request,'注册成功',_message)    # 注册成功页面跳转

    _result = {
            'success' : _state['success'],
            'message' : _state['message'],
            'form' : {
                    'username' : _userinfo['username'],
                    'realname' : _userinfo['realname'],
                    'email' : _userinfo['email'],
                }
        }

    # body content
    _template = loader.get_template('signup.html')
    _context = {
        'page_title' : '注册',
        'state' : _result,
        }
    _output = _template.render(_context)  
    return HttpResponse(_output)
    

# 退出登录
def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''
    
    return HttpResponseRedirect('/')

#编辑个人信息
def settings(request):
    # check is login
    _islogin = __is_login(request)

    
    if(not _islogin):
        return HttpResponseRedirect('/signin/')
    
    _user_id = __user_id(request)
    try:
        _login_user = User.objects.get(id=_user_id)
        _login_user_friend_list = _login_user.friend.all()  # 获取登录用户的朋友列表
        # 获取未读消息
        notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
        notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
        notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
        notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
        notice_poll_like = notice_like + notice_poll
        _friends = _login_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]

    except:
        return HttpResponseRedirect('/signin/')
    
    if request.method == "POST":
        # get post params
        _userinfo = {
            'realname' : request.POST['realname'],         
            'url' : request.POST['url'],
            'email' : request.POST['email'],
            'face' : request.FILES.get('face',None),  #获取上传的文件对象
            "about" : request.POST['about'],
            'sex':request.POST['sex'],
            'signs':request.POST.getlist('sign'),
        }
        _is_post = True
    else:     
        _is_post = False
    
    _state = {
        'message' : ''
    }

    signs=_login_user.sign.split(';')   #标签数组
    
    # save user info
    if _is_post:
        _login_user.realname = _userinfo['realname']
        _login_user.url = _userinfo['url']
        _login_user.email = _userinfo['email']
        _login_user.about = _userinfo['about']
        _login_user.sex=_userinfo['sex']
        labels=''
        signs=_userinfo['signs']
        for label in _userinfo['signs']:
            labels+=label+';'
        _login_user.sign=labels    #保存标签

        _file_obj = _userinfo['face']
        # try:
        if _file_obj:
            _upload_state = uploader.upload_face(_file_obj)    #保存上传文件
            if _upload_state['success']:
                _login_user.face = _upload_state['message']             #配置图片文件路径
            else:
                return __result_message(request,_('Error'),_upload_state['message'])

        _login_user.save(False)      #保存图片路径到数据库
        _state['message'] = _('Successed.')
        # except:
            # return __result_message(request,u'错误','提交数据时出现异常，保存失败。')

    #返回标签数组
    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    # body content
    _template = loader.get_template('settings.html')
    _context = {
        'page_title' : _('Profile'),
        'state' : _state,
        'islogin' : _islogin,
        'user' : _login_user,
        'login_user':_login_user,
        'friends':_friends,
        'login_user_friend_list':_login_user_friend_list,
        'notice_poll_like':notice_poll_like,
        'notice_tread':notice_tread,
        'notice_comment':notice_comment,
        'signs':signs,     #标签数组
        'logger':logger,
        }
    _output = _template.render(_context)  
    return HttpResponse(_output)
    
# 查询指定页的用户列表
def users_index(request):
    return users_list(request,1)     # 显示第一页的用户
    
# all users list
def users_list(request,_page_index=1):

    # check is login
    _islogin = __is_login(request)       #检查是否登录

    try:
        _user = User.objects.get(id=__user_id(request))  # 获取当前登录的用户
    except:
        return HttpResponseRedirect('/signin/')

    _page_title = _('Everyone')
    _users = User.objects.order_by('-addtime')

    _login_user = None
    _login_user_friend_list = None
    _friends=None

    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))   #获取当前登录用户
            _login_user_friend_list = _login_user.friend.all()    #用多对多关系查询所有朋友
            _friends = _login_user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]
        except:
            _login_user = None

    # 分页
    _page_bar = formatter.pagebar(_users,_page_index,'','control/userslist_pagebar.html')
    
    # 计算当前页的其实记录
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)

    # 获取当前页的用户
    _users = _users[_offset_index:_last_item_index]

    #获取未阅读消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    # body content
    _template = loader.get_template('users_list.html')

    _context = {
        'page_title' : _page_title,
        'users' : _users,
        'login_user_friend_list' : _login_user_friend_list,
        'islogin' : _islogin,
        'userid' : __user_id(request),
        'page_bar' : _page_bar,
        'user':_user,
        'login_user':_login_user,
        'notice_poll_like':notice_poll_like,
        'notice_comment':notice_comment,
        'notice_tread':notice_tread,
        'friends':_friends,
        'logger':logger,
        'online_num': online_num,  # 在线人数
         'user_num': user_num,
        'lastday_num': lastday_num,
        'today_num': today_num,
        }
    
    _output = _template.render(_context)    
    
    return HttpResponse(_output)

# 添加好友
def friend_add(request,_username):
    
    # check is login
    _islogin = __is_login(request)
    
    if(not _islogin):
        return HttpResponseRedirect('/signin/')
    
    _state = {
        "success" : False,
        "message" : "",
    }
    
    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return __result_message(request,_('Sorry'), _('Sorry.This user dose not exist.'))
           
    # check friend exist
    try:
        _friend = User.objects.get(username=_username)
        _user.friend.add(_friend)
        try:
            notice=Notice_friend(sender=_user,receiver=_friend,type=4)     #记录是谁添加谁的
            notice.save()
            _user.grade += 2
            _friend.grade += 2
            _user.logger += 'add friend %s +2;' % _friend.username
            _friend.logger += '%s add you as friend +2;' % _user.username
            _user.friend_num += 1
            _friend.friend_num += 1
            _user.save()
            _friend.save()
        except:
            pass
        return __result_message(request,_('Successed'), _('Happy, %s is your friend now.\n Keep your relationship or you will be droped RP points.')% _friend.username)
    except:
        return __result_message(request,_('Sorry'), _('This user does not exist.'))
    
def friend_remove(request,_username):
    """
    summary:
        解除与某人的好友关系
    """
    # check is login
    _islogin = __is_login(request)

    if(not _islogin):
        return HttpResponseRedirect('/signin/')
    
    _state = {
        "success" : False,
        "message" : "",
    }
    
    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return __result_message(request,_('Sorry'), _('This user dose not exist.'))
           
    # check friend exist
    try:
        _friend = User.objects.get(username=_username)
        _user.friend.remove(_friend)
        try:
            find_notice=Notice_friend.objects.get(sender=_user,receiver=_friend)  #主动解除关系
            find_notice.delete()    #删除记录
            _user.grade-=3
            _friend.grade-=2
            _user.friend_num-=1
            _friend.friend_num-=1
            _user.logger+='remove %s -3;'%_friend.username
            _friend.logger+='removed by %s  -2;'%_user.username
            _user.save()
            _friend.save()
            #分数记录
        except:
            try:
                find_notice=Notice_friend.objects.get(sender=_friend,receiver=_user)  #被动解除关系
                find_notice.delete()
                _user.grade -= 5
                _friend.grade -= 3
                _user.friend_num -= 1
                _friend.friend_num -= 1
                _user.logger += '你被 %s 删除 -5;' % _friend.username
                _friend.logger += '你删除了 %s -3;' % _user.username
                _user.save()
                _friend.save()
                #分数记录
            except:
                pass
        return __result_message(request,_('Successed'), _('%s has been removed.But your RP points also will drop.') % _friend.realname)
    except:
        return __result_message(request,_('Undisposed'), 'Sorry,He/She does not your friend.')

def api_note_add(request):
    """
    summary:
        api interface post message
    params:
        GET['uname'] Tmitter user's username
        GET['pwd'] user's password not encoding
        GET['msg'] message want to post
        GET['from'] your web site name
    author:
        Jason Lee
    """
    # get querystring params
    _username = request.GET['uname']    
    _password = function.md5_encode(request.GET['pwd'])
    _message = request.GET['msg']
    _from = request.GET['from']
    
    # Get user info and check user
    try:
        _user = User.objects.get(username=_username,password=_password)        
    except:
        return HttpResponse("-2")
    
    # Get category info ,If it not exist create new
    (_cate,_is_added_cate) = Category.objects.get_or_create(name=_from)
    
    try:
        _note = Note(message=_message,user=_user,category=_cate)
        _note.save()
        return HttpResponse("1")
    except:
        return HttpResponse("-1")

# 页面测试
def bootstrap_test(request):
    _template=loader.get_template('index1.html')
    return HttpResponse(_template.render())


# 消息详细内容
def detail(request,_id):
   return comment_page(request,_id,1)

#对消息进行评论
def comment_page(request,_note_id,_page_index):

    _islogin=__is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'),'请先登录在评论')

    _user_id=__user_id(request)    #登录的用户
    _content=''

    _offset_index=(int(_page_index)-1)*PAGE_SIZE
    _last_item_index=PAGE_SIZE*int(_page_index)

    _login_user=User.objects.get(username=__user_name(request))


    try:
        _content=request.POST['content']
        _is_post=True
    except KeyError:
        _is_post=False

    _user = User.objects.get(id=_user_id)
    _note = Note.objects.get(id=_note_id)
    _friends = _user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]

    if _is_post:    #发表评论
        try:
            #_user = User.objects.get(id=_user_id)
            #_note = Note.objects.get(id=_note_id)
            _comment=Comment(user=_user,note=_note,content=_content)
            _comment.save()
            _note.comment_num+=1    #更新评论数
            _note.repeat_num=get_note_scancount(request,_note_id)  #更新浏览数
            _note.save()
            return HttpResponseRedirect('/message/'+_note_id)    #返回消息的页面
        except:
            return __result_message(request, _('Sorry'), '用户不存在')

    #获取评论列表，转到detail页面
    _rootComments=Comment.objects.filter(note=_note,comment_parent=None).order_by('-pub_date')   #获取所有根评论
    _childComments=Comment.objects.exclude(note=_note,comment_parent=None).order_by('-pub_date') #获取所有子评论
    #获取根评论的子评论
    comments_tree=collections.OrderedDict()
    #childs = list(_childComments)
    roots=list(_rootComments)
    for root in roots:
        childs = list(_childComments)
        comments_tree[root]=find_child(root,childs,[])

    #获取未阅读的消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']


    _page_bar=formatter.pagebar(_rootComments,_page_index,note_id=_note_id)

    _comments=_rootComments[_offset_index:_last_item_index]

    _template=loader.get_template('detail.html')

    _context={
        'page_title':'评论',
        'comments':_comments,    #根评论
        'page_bar':_page_bar,
        'islogin':_islogin,
        'user':_user,
        'login_user':_login_user,
        'userid':__user_id(request),
        'item':_note,
        'friends':_friends,
        'note_id':_note_id,
        'page_index':_page_index,
        'comments_tree':comments_tree,
        'notice_comment':notice_comment,
        'notice_tread':notice_tread,
        'notice_poll_like':notice_poll_like,
        'notice_poll':notice_poll,
        'notice_like':notice_like,
        'logger':logger,
        'online_num': online_num,  # 在线人数
         'user_num': user_num,
        'lastday_num': lastday_num,
        'today_num': today_num,

    }
    _output = _template.render(_context)

    return HttpResponse(_output)

#寻找根评论的子评论
def find_child(root,child,root_child):
    for c in child:
        if c.comment_parent == root:
            root_child.append(c)
            #child.remove(c)
            find_child(c, child, root_child)
    return root_child

#统计当前在线人数（5分钟内，中间件在middle.py）
def get_online_count():
    online_ips=cache.get('online_ips',[])
    if online_ips:
        online_ips=cache.get_many(online_ips).keys()
        return len(online_ips)
    return 0

#返回用户数，昨日消息数，今日消息数
def get_info():
    oneday=timedelta(days=1)
    today=now().date()
    lastday=today-oneday
    todayend=today+oneday
    user_num=User.objects.count()
    #使用缓存
    lastday_num=cache.get('lastday_num',None)
    today_num=cache.get('today_num',None)

    if lastday_num is None:
        lastday_num=Note.objects.filter(addtime__range=[lastday,today]).count()
        cache.set('lastday_num',lastday_num,60*60)    #缓存60分钟，即一个小时

    if today_num is None:
        today_num=Note.objects.filter(addtime__range=[today,todayend]).count()
        cache.set('today_num',today_num,60*60)

    loginUser=get_online_count()

    info={
        'loginUser':loginUser,     #在线人数
        'user_num':user_num,       #总用户数
        'lastday_num':lastday_num,    #昨天消息数
        'today_num':today_num,       #今日消息数
    }
    return info

#返回消息的浏览数
def get_note_scancount(request,_note_id):

    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip=request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip=request.META['REMOTE_ADDR']
    visit_ips=cache.get(_note_id,[])
    _note=Note.objects.get(id=_note_id)

    if ip not in visit_ips:
        _note.browse_num+=1
        _note.save()
        visit_ips.append(ip)
    cache.set(_note_id,visit_ips,60*10)   #访问有效时间为10分钟，缓存默认为本地系统
    return _note.browse_num


#点赞消息
def poll_note(request,_id):

    _note_id=_id

    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在点赞')

    _user_id = __user_id(request)  # 登录的用户
    note=None
    num=0
    haspoll=0
    try:
        user=User.objects.get(id=_user_id)
        note=Note.objects.get(id=_note_id)
        try:
            haspoll=PollNote.objects.filter(user=user,note=note).count()
            if haspoll:
                return HttpResponse(str(note.poll_num))    #已经点赞过了
            else:
                pollNote=PollNote(user=user,note=note,ifpoll=True)
                note.poll_num+=1
                note.user.grade+=1   #点赞rp加1
                note.user.logger+='%s thumb up your note +1;'%user.username
                note.user.save()
                pollNote.save()
                note.save()
                num=note.poll_num
        except:
            __result_message(request, _('Sorry'), '查找失败')
    except:
        pass
    return HttpResponse(str(num))

#踩消息
def tread_note(request,_id):

    _note_id=_id

    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在点赞')

    _user_id = __user_id(request)  # 登录的用户
    note=None
    num=0
    haspoll=0
    try:
        user=User.objects.get(id=_user_id)
        note=Note.objects.get(id=_note_id)
        try:
            haspoll=ThreadNote.objects.filter(user=user,note=note).count()
            if haspoll:
                return HttpResponse(str(note.tread_num))    #已经踩过了
            else:
                treadNote=ThreadNote(user=user,note=note,ifthread=True)
                note.tread_num+=1
                note.user.grade-=1
                note.user.logger+='%s tread your note -1;'%user.username
                note.user.save()
                treadNote.save()
                note.save()
                num=note.tread_num
        except:
            __result_message(request, _('Sorry'), '查找失败')
    except:
        pass
    return HttpResponse(str(num))

#点赞评论
def like_comment(request,_id):

    _comment_id=_id

    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在点赞')

    _user_id = __user_id(request)  # 登录的用户
    note=None
    num=0
    haspoll=0
    try:
        user=User.objects.get(id=_user_id)
        comment=Comment.objects.get(id=_comment_id)
        try:
            haspoll=PollComment.objects.filter(user=user,comment=comment).count()
            if haspoll:
                return HttpResponse(str(comment.poll_num))    #已经点赞过了
            else:
                pollComment=PollComment(user=user,comment=comment,ifpoll=True)
                comment.poll_num+=1
                comment.user.grade+=1
                comment.user.logger+='%s like your comment +1;'%user.username
                comment.user.save()
                pollComment.save()
                comment.save()
                num=comment.poll_num
        except:
            __result_message(request, _('Sorry'), '查找失败')
    except:
        pass
    return HttpResponse(str(num))

#测试ajax
def test_ajax(request):

    _template = loader.get_template('UI.html')

    _output = _template.render()

    return HttpResponse(_output)


#回复评论
def comment_reply(request,_id):

    _comment_id=_id

    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在回复')

    _user_id = __user_id(request)  # 登录的用户
    _content_reply=None
    try:
        _content_reply=request.POST['content_reply']
        _is_post=True
    except KeyError:
        _is_post=False

    if _is_post:
        user=User.objects.get(id=_user_id)
        comment=Comment.objects.get(id=_comment_id)
        note=comment.note
        reply=Comment(user=user,comment_parent=comment,note=note,content=_content_reply)
        reply.save()
        comment.reply_num+=1
        comment.save()

    return HttpResponseRedirect(function.get_referer_url(request))   #重定向原来的页面

#展示未读的评论
def notice_comment_list(request,_username):
    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在操作')

    _user_id = __user_id(request)  # 登录的用户
    _content = ''

    _login_user = User.objects.get(username=__user_name(request))
    _friends=_login_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]   #获取朋友列表

    #获取未读消息
    unread_notices=Notice.objects.filter(receiver=_login_user,status=False).order_by('-create_date')
    unread_num=Notice.objects.filter(receiver=_login_user,status=False).count()

    unread_id=[]
    for unread in unread_notices:
        unread_id.append(unread.id)

    #将未读消息改为已读消息
    for _unread in unread_notices:
        _unread.status=True
        _unread.save()

    #获取通知栏
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    size=PAGE_SIZE
    _page_index=1    #默认为第一页
    _offset_index = (int(_page_index) - 1) * size
    _last_item_index = size * int(_page_index)
    unread_notice = unread_notices[_offset_index:_last_item_index]

    _template = loader.get_template('notice_comment_list.html')

    _context = {
        'page_title': '未读评论',
        'islogin': _islogin,
        'login_user': _login_user,
        'userid': __user_id(request),
        'friends': _friends,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'notice_poll': notice_poll,
        'notice_like':notice_like,
        'unread_notice':unread_notice,
        'unread_num':unread_num,    #返回未读消息的总数
        'user':_login_user,
        'unread_id':json.dumps(unread_id),
        'logger':logger,
        'online_num': online_num,  # 在线人数
        'user_num': user_num,
        'lastday_num': lastday_num,
        'today_num': today_num,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)

#展示未读消息的赞
def notice_poll_list(request,_username):
    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在操作')

    _user_id = __user_id(request)  # 登录的用户
    _content = ''

    _login_user = User.objects.get(username=__user_name(request))
    _friends = _login_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]  # 获取朋友列表

    #获取消息的赞
    note_notices = Notice_poll.objects.filter(receiver=_login_user, status=False).order_by('-create_date')

    unread_num = Notice_poll.objects.filter(receiver=_login_user, status=False).count()

    unread_id = []
    for unread in note_notices:
        unread_id.append(unread.id)

    # 将未读消息改为已读消息
    for _unread in note_notices:
        _unread.status = True
        _unread.save()

    # 获取通知栏
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    size =PAGE_SIZE
    _page_index = 1  # 默认为第一页
    _offset_index = (int(_page_index) - 1) * size
    _last_item_index = size * int(_page_index)
    unread_notice = note_notices[_offset_index:_last_item_index]

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    _template = loader.get_template('notice_poll_list.html')

    _context = {
        'page_title': '未读评论',
        'islogin': _islogin,
        'login_user': _login_user,
        'userid': __user_id(request),
        'friends': _friends,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'notice_poll_like': notice_poll_like,
        'unread_notice': unread_notice,
        'unread_num': unread_num,  # 返回未读消息的总数
        'user': _login_user,
        'unread_id': json.dumps(unread_id),
        'notice_poll':notice_poll,
        'logger':logger,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)

#展示未读评论的踩
def notice_tread_list(request,_username):
    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在操作')

    _user_id = __user_id(request)  # 登录的用户
    _content = ''

    _login_user = User.objects.get(username=__user_name(request))
    _friends = _login_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]  # 获取朋友列表

    #获取消息的赞
    note_notices = Notice_tread.objects.filter(receiver=_login_user, status=False).order_by('-create_date')

    unread_num = Notice_tread.objects.filter(receiver=_login_user, status=False).count()

    unread_id = []
    for unread in note_notices:
        unread_id.append(unread.id)

    # 将未读消息改为已读消息
    for _unread in note_notices:
        _unread.status = True
        _unread.save()

    # 获取通知栏
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    size = PAGE_SIZE
    _page_index = 1  # 默认为第一页
    _offset_index = (int(_page_index) - 1) * size
    _last_item_index = size * int(_page_index)
    unread_notice = note_notices[_offset_index:_last_item_index]

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    _template = loader.get_template('notice_tread_list.html')

    _context = {
        'page_title': '未读评论',
        'islogin': _islogin,
        'login_user': _login_user,
        'userid': __user_id(request),
        'friends': _friends,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'notice_poll_like': notice_poll_like,
        'unread_notice': unread_notice,
        'unread_num': unread_num,  # 返回未读消息的总数
        'user': _login_user,
        'unread_id': json.dumps(unread_id),
        'logger':logger,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)

#展示未读评论的赞
def notice_like_list(request,_username):
    _islogin = __is_login(request)
    if not _islogin:
        __result_message(request, _('Sorry'), '请先登录在操作')

    _user_id = __user_id(request)  # 登录的用户
    _content = ''

    _login_user = User.objects.get(username=__user_name(request))
    _friends = _login_user.friend.order_by('-addtime')[0:FRIEND_LIST_MAX]  # 获取朋友列表

    #获取消息的赞
    note_notices = Notice_like.objects.filter(receiver=_login_user, status=False).order_by('-create_date')

    unread_num = Notice_like.objects.filter(receiver=_login_user, status=False).count()

    unread_id = []
    for unread in note_notices:
        unread_id.append(unread.id)

    # 将未读消息改为已读消息
    for _unread in note_notices:
        _unread.status = True
        _unread.save()

    # 获取通知栏
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    size = PAGE_SIZE
    _page_index = 1  # 默认为第一页
    _offset_index = (int(_page_index) - 1) * size
    _last_item_index = size * int(_page_index)
    unread_notice = note_notices[_offset_index:_last_item_index]

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    _template = loader.get_template('notice_like_list.html')

    _context = {
        'page_title': '未读评论',
        'islogin': _islogin,
        'login_user': _login_user,
        'userid': __user_id(request),
        'friends': _friends,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'notice_poll_like': notice_poll_like,
        'unread_notice': unread_notice,
        'unread_num': unread_num,  # 返回未读消息的总数
        'user': _login_user,
        'unread_id': json.dumps(unread_id),
        'logger':logger,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)

#加载评论数据
def load_more_data(request,type):

    _page_index=request.GET['time']
    unread_id=None
    unread_id=request.GET['unread_id']
    #unread_id = unread_id.replace("%2C", ",")

    type=int(type)

    unread_id=unread_id.split(',')
    ids = []
    for id in unread_id:
        if id.isdigit():
            ids.append(int(id))

    _login_user = User.objects.get(username=__user_name(request))
    unread_notices=[]
    if type==0:    #评论
        unread_notices = Notice.objects.filter(id__in=ids).order_by('-create_date')
    elif type==1:   #消息赞
        unread_notices = Notice_poll.objects.filter(id__in=ids).order_by('-create_date')
    elif type==2:    #消息踩
        unread_notices = Notice_tread.objects.filter(id__in=ids).order_by('-create_date')
    elif type==3:    #评论赞
        unread_notices = Notice_like.objects.filter(id__in=ids).order_by('-create_date')

    size = PAGE_SIZE
    _offset_index = (int(_page_index) - 1) * size
    _last_item_index = size * int(_page_index)
    unread_notice = unread_notices[_offset_index:_last_item_index]

    _template = loader.get_template('loadMore/comment.html')
    if type==0:
        _template = loader.get_template('loadMore/comment.html')
    elif type==1:
        _template = loader.get_template('loadMore/poll.html')
    elif type==2:
        _template=loader.get_template('loadMore/tread.html')
    elif type==3:
        _template=loader.get_template('loadMore/like.html')

    _context = {
        'unread_notice': unread_notice,
        'unread_id':ids,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)



#搜索用户
def search(request):
    return search_index(request,1)

def search_index(request,_page_index=1):

    _islogin = __is_login(request)  # 检查是否登录
    _search=''
    try:
        _search=request.POST['search_username']
        is_post=True
    except KeyError:
        is_post=False

    if not is_post:
        return HttpResponseRedirect('/')   #重定向回主页

    try:
        _user = User.objects.get(id=__user_id(request))  # 获取当前登录的用户
    except:
        return HttpResponseRedirect('/signin/')

    _page_title = _('Search')
    _users = User.objects.filter(username__contains=_search).order_by('-addtime')

    _login_user = None
    _login_user_friend_list = None
    _friends = None

    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))  # 获取当前登录用户
            _login_user_friend_list = _login_user.friend.all()  # 用多对多关系查询所有朋友
            _friends = _login_user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]
        except:
            _login_user = None

    # 分页
    _page_bar = formatter.pagebar(_users, _page_index, '', 'control/searchlist_pagebar.html')

    # 计算当前页的其实记录
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)

    # 获取当前页的用户
    _users = _users[_offset_index:_last_item_index]

    # 获取未阅读消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    # body content
    _template = loader.get_template('users_list.html')

    _context = {
        'page_title': _page_title,
        'users': _users,
        'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
        'page_bar': _page_bar,
        'user': _user,
        'login_user': _login_user,
        'notice_poll_like': notice_poll_like,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'friends': _friends,
        'logger':logger,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)

#我的好友列表
def myfriends(request):
    return myfriends_index(request,1)

def myfriends_index(request,_page_index=1):

    _islogin = __is_login(request)  # 检查是否登录
    _search = ''

    if not _islogin:
        return HttpResponseRedirect('/signin/')

    try:
        _user = User.objects.get(id=__user_id(request))  # 获取当前登录的用户
    except:
        return HttpResponseRedirect('/signin/')

    _page_title = _('myfrinds')

    _login_user = None
    _login_user_friend_list = None
    _friends = None

    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))  # 获取当前登录用户
            _login_user_friend_list = _login_user.friend.all()  # 用多对多关系查询所有朋友
            _friends = _login_user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]
            _users=_login_user_friend_list
        except:
            _login_user = None

    # 分页
    _page_bar = formatter.pagebar(_users, _page_index, '', 'control/myfriendslist_pagebar.html')

    # 计算当前页的其实记录
    _offset_index = (int(_page_index) - 1) * PAGE_SIZE
    _last_item_index = PAGE_SIZE * int(_page_index)

    # 获取当前页的用户
    _users = _users[_offset_index:_last_item_index]

    # 获取未阅读消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    # body content
    _template = loader.get_template('users_list.html')

    _context = {
        'page_title': _page_title,
        'users': _users,
        'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
        'page_bar': _page_bar,
        'user': _user,
        'login_user': _login_user,
        'notice_poll_like': notice_poll_like,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'friends': _friends,
        'logger':logger,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)

#RP榜
def rp_range(request):

    _islogin = __is_login(request)  # 检查是否登录
    _search = ''

    _page_title = 'rp榜'

    _login_user = None
    _login_user_friend_list = None
    _friends = None

    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))  # 获取当前登录用户
            _login_user_friend_list = _login_user.friend.all()  # 用多对多关系查询所有朋友
            _friends = _login_user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]
            _users = _login_user_friend_list
        except:
            _login_user = None

    # 获取未阅读消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    users=User.objects.order_by('-grade')[:20]

    # body content
    _template = loader.get_template('rp_list.html')

    _context = {
        'page_title': _page_title,
        'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
        'user': _login_user,
        'login_user': _login_user,
        'notice_poll_like': notice_poll_like,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'friends': _friends,
        'logger': logger,
        'users':users,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)

#好友推荐
def recommend(request):

    _islogin = __is_login(request)  # 检查是否登录
    _search = ''

    if not _islogin:
        return HttpResponseRedirect('/signin/')

    _login_user = None
    _login_user_friend_list = None
    _friends = None

    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))  # 获取当前登录用户
            _login_user_friend_list = _login_user.friend.all()  # 用多对多关系查询所有朋友
            _friends = _login_user.friend.order_by("-addtime")[0:FRIEND_LIST_MAX]
            _users = _login_user_friend_list
        except:
            _login_user = None

    # 获取未阅读消息
    notice_comment = Notice.objects.filter(receiver=_login_user, status=False).count()
    notice_poll = Notice_poll.objects.filter(receiver=_login_user, status=False).count()
    notice_tread = Notice_tread.objects.filter(receiver=_login_user, status=False).count()
    notice_like = Notice_like.objects.filter(receiver=_login_user, status=False).count()
    notice_poll_like = notice_like + notice_poll

    logger = []
    if _login_user:
        logger = list(reversed(_login_user.logger.split(';')))[:15]

    system_info = get_info()
    online_num = system_info['loginUser']
    user_num = system_info['user_num']
    lastday_num = system_info['lastday_num']
    today_num = system_info['today_num']

    #获取用户标签
    signs=_login_user.sign.split(';')
    all_users = User.objects.filter(sign__contains=signs[0])
    for sign in signs:
        if sign:
            users = User.objects.filter(sign__contains=sign)
            all_users = all_users | users


    # body content
    _template = loader.get_template('users_list.html')

    _context = {
        'page_title': '用户推荐',
        'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
        'user': _login_user,
        'login_user': _login_user,
        'notice_poll_like': notice_poll_like,
        'notice_comment': notice_comment,
        'notice_tread': notice_tread,
        'friends': _friends,
        'logger': logger,
        'users': all_users,
    'online_num': online_num,  # 在线人数
    'user_num': user_num,
    'lastday_num': lastday_num,
    'today_num': today_num,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)









