#!usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
import re

class MiddlewareMixin(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super(MiddlewareMixin, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class Middle(MiddlewareMixin):  # 必须去继承这个类
    def process_request(self, request):
        current_url = request.path_info  # 获取当前请求的路径

        # 如果匹配的是白名单里面的就让通过，不需要权限
        for url in settings.WHITE_LIST:
            if re.match(url, current_url):
                return None
        permission_dict = request.session.get(settings.PERMISSION_URL_DICT)  # 获取session
        if not permission_dict:  # 如果没有得到，就直接跳转到login页面
            return redirect("/login/")

        flag = False
        for group_id, code_url in permission_dict.items():
            for db_url in code_url["urls"]:
                regex = "^{0}$".format(db_url)

                # 因为match匹配的时候会把你只要有的都匹配到了，我们只匹配当前的url，所以得加一个起始终止符
                if re.match(regex, current_url):
                    request.permission_code_url = code_url["code"]  # 用户输入的url和数据库的url匹配成功之后成功之后先把code保存在request中，方便以后判断
                    flag = True
                    break  # 如果匹配成功就进入页面
                    # 注意在这里不能用return，在中间件中process_request这个函数如果有return就只会执行自己的
                    #   response和上面的response,不会执行后续的。没有return就会去继续执行后续中间件和视图函数
            if flag:  # 结束外层循环
                break
        if not flag:
            return redirect('/403.html')  # 如果访问不成功就显示无权访问

    def process_reponse(self, request, response):
        return response
