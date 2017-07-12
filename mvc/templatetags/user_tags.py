# -*- coding: utf-8 -*-
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from mvc.models import *
from settings import *
import re
import markdown2


# 编写自定义的过滤器
register = Library()

def get_face_url(size,content):
    if content:
        return MEDIA_URL + 'face/%d/%s' % (size, content)
    else:
        return DEFAULT_FACE % (size)

def face16(content):
    return get_face_url(16,content)

def face24(content):
    return get_face_url(24,content)

def face32(content):
    return get_face_url(32,content)

def face(content):
    return get_face_url(75,content)

#使得输出时候能够显示多个空格
@stringfilter
def spacify(value,autoescape=None):
    if autoescape:
        esc=conditional_escape
    else:
        esc=lambda x:x
    return mark_safe(
        re.sub(r'[\t\r\v\f]','&'+'nbsp;',esc(value))
    )
spacify.needs_autoescape=True

#将文本应用于markdown2，无用？
def Tmarkdown2(content):
    content=markdown2.markdown(content)
    return content


register.filter('face', face)
register.filter('face16', face16)
register.filter('face24', face24)
register.filter('face32', face32)
register.filter('spacify',spacify)
register.filter('Tmarkdown2',Tmarkdown2)



def user_url(username):
    return '%suser/%s' % (APP_DOMAIN,username)