#-*- coding:utf-8 -*-
'''
自定义的中间件
中间件查看：http://code.ziqiangxuetang.com/django/django-middleware.html
兼容1.10和1.9以前的版本

要想一次获取多个缓存值，可以使用 cache.get_many() 。如果可能的话，对于给定的缓存后端， 
get_many() 将只访问缓存一次，而不是对每个缓存键值都进行一次访问。
 get_many() 所返回的字典包括了你所请求的存在于缓存中且未超时的所有键值。 
 
'''
from django.core.cache import cache

try:
    from django.utils.deprecation import MiddlewareMixin   #1.10.x
except ImportError:
    MiddlewareMixin=object   #1.4.x-1.9.x

class CommonMiddleware(MiddlewareMixin):
    def process_request(self,request):
        #获取用户IP
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip=request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip=request.META['REMOTE_ADDR']
        online_ips=cache.get('online_ips',[])
        if online_ips:
            online_ips=cache.get_many(online_ips).keys()

        cache.set(ip,0,5*60)
        if ip not in online_ips:
             online_ips.append(ip)
        cache.set('online_ips',online_ips)