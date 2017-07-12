#-*- coding:utf-8 -*-
import collections
# Create your tests here.
from wsgi import *
import django
import json
django.setup()
from mvc.models import User
import md5

signs=['娱乐','艺术','睡觉']
user =User.objects.get(username='foo')

s=md5.new(user.password).hexdigest()

print(user.password)
print(s)
