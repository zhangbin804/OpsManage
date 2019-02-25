from django.shortcuts import render, HttpResponse, redirect
from ManageOps import models
from rbac import models as rbac_models
import re
import os
import json
import time
from django.http import QueryDict
from django.views import View
from django.forms import widgets, fields
from ManageOps.ansible.ansible import Git,Shell,Ansible
from ManageOps.src import page
from django.utils.safestring import mark_safe
from ManageOps.src import dingding,aliyun_slb
from django.conf import settings
from rbac.init_permission import init_permission
from ManageOps.FROM import NewPassword


def auth_character(args):
    character = re.findall(r'[\'\"\\\#\(\)/]', args)
    return bool(character)


class Login(View):
    def get(self, request):
        msg = ''
        return render(request, 'login.html', {'msg': msg})
    def post(self, request):
        username = request.POST.get('user')
        password = request.POST.get('password')
        user = rbac_models.UserInfo.objects.filter(name=username, password=password).first()
        if user:
            init_permission(user, request)
            return redirect('/index/')
        else:
            msg = '账号或密码错误'
            return render(request, 'login.html', {'msg': msg})


def auth(func):
    def inner(request, *args, **kwargs):
        is_login = request.session.get('is_login', False)
        if is_login:
            return func(request, *args, **kwargs)
        else:
            return redirect('/login/')

    return inner

@auth
def index(request):
    username = request.session.get('user')
    return render(request, 'index.html', {'username': username})

@auth
def logout(request):
    del request.session["is_login"]
    return redirect('/index/')

@auth
def change_password(request):
    username = request.session.get('user')
    if request.method == "GET":

        obj = NewPassword()
        return render(request, "change_password.html", {'obj': obj, 'username': username})
    elif request.method == "POST":
        obj = NewPassword(request.POST)
        if obj.is_valid():
            password = obj.clean()["old_password"]
            user = request.session.get('user')
            username = rbac_models.UserInfo.objects.filter(name=user, password=password)
            if username:
                if obj.clean()["new_password"] == obj.clean()["new_password2"]:
                    rbac_models.UserInfo.objects.filter(name=user).update(password=obj.clean()["new_password"])

                    return redirect('/logout/')
                else:
                    return render(request, "change_password.html", {'obj': obj, 'username': username})
            else:
                password_error = '密码错误!'
                return render(request, "change_password.html", {'password_error': password_error, 'username': username})
        else:
            return render(request, 'change_password.html', {'obj': obj, 'username': username})
    return render(request, 'change_password.html', {'username': username})

@auth
def git_code(request):
    username = request.session.get('user')
    current_page = request.GET.get('p', 1)

    current_page = int(current_page)
    total_count = models.Code_version.objects.all().count()
    obj = page.PagerHelper(total_count, current_page, '/git_code', 10)
    pager = obj.pager_str()
    cls_list = models.Code_version.objects.all()[obj.db_start:obj.db_end]
    last_integer = total_count // 10
    last_remainder = total_count % 10
    if last_integer < 1:
        last_page = 1
    else:
        if last_remainder == 0:
            last_page = last_integer
        else:
            last_page = last_integer + 1

    return render(request, 'git_code.html',
                  {'cls_list': cls_list, 'pager': mark_safe(pager), 'last_page': last_page, 'username': username})

@auth
def add_web(request):
    username = request.session.get('user')
    if request.method == 'POST':
        add_www_name = request.POST.get('add_www_name')
        add_www_dir = request.POST.get('add_www_dir')
        try:
            add_www = models.Code_version.objects.create(www_name=add_www_name, www_dir=add_www_dir)
            return HttpResponse('add success')
        except Exception as e:
            return HttpResponse('0')
    return redirect('/git_code')

@auth
def delete_web(request):
    username = request.session.get('user')
    if request.method == 'GET':
        return redirect('/git_code')
    if request.method == 'POST':
        delete_web = request.POST.lists()
        for i in delete_web:
            delete_web_list = i[1]
        for del_web_name in delete_web_list:
            del_obj = models.Code_version.objects.filter(www_name=del_web_name).delete()
        return HttpResponse('delete success')

@auth
def sites_statu(request,*args,**kwargs):
    username = request.session.get('user')
    www_name = request.path.split('/')[-2]
    www = models.Code_version.objects.filter(www_name=www_name)
    if www:
        www_dir = www.values("www_dir")[0]['www_dir']
        www_git = Git(www_dir)
        fetch = www_git.fetch()
        old_version = www_git.old_versions()
        new_version = www_git.master_versions()
        www_git_10_row = www_git.git_log_version_10()
        www_git_10_row_list = www_git_10_row.strip().split('\n')
        del www_git_10_row_list[0]
        www_git_10_row_dict = {}
        for i in www_git_10_row_list:
            i = i.split(' ', 1)
            www_git_10_row_dict[i[0]] = i[1]

    return render(request, 'sites_status.html',
                  {'www_name': www_name, 'old_version': old_version, 'www_dir': www_dir, 'new_version': new_version,
                   'www_git_10_row_dict': www_git_10_row_dict, 'username': username})
#
@auth
def git_timing(request):
    username = request.session.get('user')
    cron_list = models.Cron_git.objects.all()
    code_list = models.Code_version.objects.all().values('www_name')
    return render(request,'git_timing.html',{"cron_list":cron_list,'code_list':code_list,'username': username})


@auth
def add_cron(request):
    if request.method == 'GET':
        return render(request,'403.html')
    if request.method == 'POST':
        create_time = time.strftime('%Y-%m-%d %X')
        create_user = request.session.get('user')
        add_cron_www_name = request.POST.get('add_cron_www_name')
        add_run_time = request.POST.get( 'add_run_time').replace('T'," ")
        cmd = Shell()
        user = create_user
        password = rbac_models.UserInfo.objects.filter(name=create_user).values('password')[0]['password']
        cron_at_shell_name = cmd.cmd("/bin/bash  %s/OpsManage/ManageOps/cron_shell/at_shell.sh %s %s %s %s %s "%(settings.HOME_PATH_DIR,user,password,add_cron_www_name,settings.HOME_PATH_DIR,settings.PATH_URL))
        print(cron_at_shell_name)
       # end_id = models.Cron_git.objects.all().order_by('-id')[0]
       # current_id = int(end_id.id))+1
        at_date,at_time = add_run_time.split(' ')
        at_year,at_day = at_date.split('-',1)
        at_day = at_day.replace('-','/')
        at_date_time = at_time+' '+at_day+'/'+at_year
        cron_at_task = cmd.cmd('at -f %s "%s"'%(cron_at_shell_name,at_date_time))
        #添加定时任务
        print(cron_at_shell_name)
        atq_id = int(cmd.cmd("atq |tail -1|echo -n `awk '{print $1}'`"))
        try:
            obj = models.Cron_git.objects.create(run_time=add_run_time,cron_shell_file_path=cron_at_shell_name,www_name_id=add_cron_www_name,create_username=user,create_time=create_time,atq_id=atq_id)
        except Exception as e:
            def del_atq(atq_id):
                cmd = Shell()
                del_shell_filename = cmd.cmd("at -c %s|egrep ^python3|awk '{printf $(NF-2)}'"%atq_id)
                os.remove(del_shell_filename)
                cmd.cmd('atrm %s'%atq_id)
            del_atq(atq_id)
            obj=False
        if obj:
            cron_id = models.Cron_git.objects.filter(run_time=add_run_time,www_name_id=add_cron_www_name,create_username=user,create_time=create_time,atq_id=atq_id).values("id")[0]["id"]
            with open(cron_at_shell_name,'r',encoding='utf-8') as f:
                content = f.read()
                content = content.replace('number',str(cron_id))
            with open(cron_at_shell_name,'w',encoding='utf-8') as f:
                f.write(content)
            return HttpResponse(json.dumps({'msg':'success'}))
        else:
            return HttpResponse({'msg':'error'})

@auth
def delete_cron(request,*args,**kwargs):
    if request.method == 'GET':
        return render(request,'403.html')
    if request.method == 'POST':
        del_cron_list = request.POST.lists()
        print(del_cron_list)
        def del_atq(atq_id):
            cmd = Shell()
            del_shell_filename = cmd.cmd("at -c %s|egrep ^python3|awk '{printf $(NF-2)}'"%atq_id)
            os.remove(del_shell_filename)
            cmd.cmd('atrm %s'%atq_id)

        for i in del_cron_list:
            del_cron_list = i[1]
        
        for id in del_cron_list:
            print(id)
            obj_cron = models.Cron_git.objects.filter(id=int(id))
            obj_atq_id = obj_cron.values('atq_id')[0]["atq_id"]
            del_atq(obj_atq_id)
       #     os.remove(obj_shell_filename)
            obj_cron.delete()
        return HttpResponse(json.dumps({'msg':'success'}))



@auth
def version_retreat(request):
    if request.method == 'GET':
        return redirect('/git_code')

    if request.method == 'POST':
        commit_id = request.POST.get('commit_id')
        www_name = request.POST.get('www_name')
        www_code_dir = models.Code_version.objects.filter(www_name=www_name).values('www_dir')[0]['www_dir']
        www_git = Git(www_code_dir)
        www_git.reset(commit_id)

        project = Shell()
        #代码同步带线上环境(以下脚本需要替换)
        project_cmd_str = '/bin/bash /usr/local/scripts/django_rsync_formal.sh  %s' % www_name
        project.shell(project_cmd_str)
        try:
            retreat_version = www_git.old_versions()
            date_time = time.strftime('%Y-%m-%d %X', time.localtime())
            msg = """
            版本回滚通知！
            当前时间: %s
            回滚项目: %s
            线上版本回滚为:  %s   
            """ % (date_time, www_name, retreat_version)
            if settings.DINGDING:
                dingding.sendmessage(msg)
            for k, v in settings.ECS_ID_DICT.items():
                print(k)
                # v是slb中的ecsid，#在上线代码前需要提前降低slb中对应的服务器的权重
                # k为服务器#使用ansible循环更新服务器上的代码
            return HttpResponse(json.dumps({'msg':'success'}))
        except Exception as e:
            return HttpResponse('error')
    return redirect('/index/')


@auth
def update_new_www(request):
    if request.method == 'GET':
        return redirect('/index/')
    if request.method == 'POST':
        www_name = request.POST.get('www_name')
        www_dir = models.Code_version.objects.filter(www_name=www_name).values('www_dir')[0]['www_dir']
        www_git = Git(www_dir)
        www_git.pull('origin master')
        # 执行更新的shell脚本
        project = Shell()
        # 代码同步带线上环境
        project_cmd_str = '/bin/bash /usr/local/scripts/django_rsync_formal.sh  %s'%www_name
        project.shell(project_cmd_str)
        # 发送邮件
        try:
            new_version = www_git.master_versions()
            date_time = time.strftime('%Y-%m-%d %X', time.localtime())
            msg = """
            版本上线通知！
            当前时间: %s
            上线项目: %s
            线上版本上线为:  %s   
            """ % (date_time, www_name, new_version)
            if settings.DINGDING:
                dingding.sendmessage(msg)

            return HttpResponse(json.dumps({'msg':'success'}))
        except Exception as e:
            return HttpResponse('error')
@auth
def user_info(request):
    username = request.session.get('user')
    if request.method == 'GET':
        current_page = request.GET.get('p', 1)
        current_page = int(current_page)
        total_count = rbac_models.UserInfo.objects.all().count()
        obj = page.PagerHelper(total_count, current_page, '/user_info/', 10)
        pager = obj.pager_str()
        cls_list = rbac_models.UserInfo.objects.all()[obj.db_start:obj.db_end]
        roles_list = rbac_models.Role.objects.all()[obj.db_start:obj.db_end]


        role_title_list = [cls_list[i].roles.values("title")[0]["title"] for i in range(len(cls_list))]
        #角色组并入
        last_integer = total_count // 10
        last_remainder = total_count % 10
        if last_integer < 1:
            last_page = 1
        else:
            if last_remainder == 0:
                last_page = last_integer
            else:
                last_page = last_integer + 1

        return render(request, 'user_info.html',
                      {'username': username, 'cls_list': cls_list, 'pager': mark_safe(pager), 'last_page': last_page,'role_title_list':role_title_list,'roles_list':roles_list})


def ban(request):
    return render(request, '403.html')


@auth
def add_user(request):
    if request.method == 'GET':
        return redirect('/index/')
    if request.method == 'POST':
        username = request.POST.get('add_username')
        password = request.POST.get('add_password')
        email = request.POST.get('email')
        add_user = request.POST.get('add_user')
        add_role = request.POST.get('add_role')
        try:
            user = rbac_models.UserInfo.objects.create(name=username, password=password, email=email,username=add_user)
            role = rbac_models.UserInfo.objects.filter(name=username,username=add_user).first().roles.add(add_role)
            return HttpResponse('success')
        except Exception as e:
            return HttpResponse(0)


@auth
def del_user(request):
    if request.method == 'GET':
        return redirect('/index/')
    if request.method == 'POST':
        del_user_list = request.POST.lists()
        for i in del_user_list:
            del_user_list = i[1]
        for user in del_user_list:
            obj_user = rbac_models.UserInfo.objects.filter(name=user).delete()
        return HttpResponse('del_user')

@auth
def edit_user(request,*args,**kwargs):
    username = request.session.get('user')
    user_id = int(request.path.split('/')[-2])
    roles_list = rbac_models.Role.objects.all()
    user = rbac_models.UserInfo.objects.filter(id=user_id).values("name")[0]["name"]

    return render(request,'edit_user.html',{'username': username,'user':user,'roles_list':roles_list})

@auth
def update_user(request,*args,**kwargs):
    username = request.session.get('user')
    user = request.GET.get('username', None)
    if request.method == 'GET':
        if user == None:
            return redirect('/user_info')

    if request.method == 'POST':
        update_dict = {}
        username = request.POST.get('username')
        name = request.POST.get('user')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('update_roles')


        if username:
            update_dict['username'] = username
        if email:
            update_dict['email'] = email
        if password:
            update_dict['password'] = password
        user1 = rbac_models.UserInfo.objects.filter(name=name).update(**update_dict)
        if role:
            obj = rbac_models.UserInfo.objects.filter(name=name).first()
            obj.roles.clear()
            obj.roles.add(role)
            return HttpResponse(json.dumps({'msg': 'success'}))

    return render(request, 'update_user.html', )

@auth
def update_email(request):
    username = request.session.get('user')
    if request.method == 'GET':
        email = rbac_models.UserInfo.objects.filter(name=username).values('email')[0]['email']
        return render(request, 'update_email.html', {'username': username, 'email': email})
    if request.method == 'POST':
        user = request.POST.get('username')
        email = request.POST.get('email')
        auth_email = auth_character(email)
        if  auth_email:
            return HttpResponse('非法字符')
        else:
            rbac_models.UserInfo.objects.filter(name=user).update(email=email)
            return HttpResponse(json.dumps({"msg":"success"}))


@auth
def ssh_user(request):
    username = request.session.get('user')
    if request.method == 'GET':
        web_server_list = models.Linux_server.objects.values('server_name')
        current_page = request.GET.get('p', 1)
        current_page = int(current_page)
        total_count = models.Ssh_user.objects.all().count()
        obj = page.PagerHelper(total_count, current_page, '/ssh_user', 10)
        pager = obj.pager_str()
        cls_list = models.Ssh_user.objects.all()[obj.db_start:obj.db_end]
        last_integer = total_count // 10
        last_remainder = total_count % 10
        if last_integer < 1:
            last_page = 1
        else:
            if last_remainder == 0:
                last_page = last_integer
            else:
                last_page = last_integer + 1
        return render(request, 'linux_server_user.html',
                      {'cls_list': cls_list, 'pager': mark_safe(pager), 'last_page': last_page, 'username': username,
                       'web_server_list': web_server_list})

    return render(request, 'linux_server_user.html', {'username': username, 'web_server_list': web_server_list})


@auth
def add_ssh_user(request):
    request_copy = QueryDict.copy(request.POST)
    host_list = request_copy.popitem()[1]
    add_ssh_user = request.POST.get('add_username')
    add_ssh_password = request.POST.get('add_password')
    print(add_ssh_user,add_ssh_password,host_list)
    host_list_str = ''
    for host in host_list:
        if host_list_str:
            host_list_str = host_list_str + ',' + host
        else:
            host_list_str = host
    ansible = Ansible()
    # 添加ssh账号
    ansible.add_user(host_list_str, username=add_ssh_user, password=add_ssh_password)
    shell_cmd = Shell()
    add_password = 'ansible %s -m shell -a \"echo \'%s\'|passwd --stdin %s \" ' % (host_list_str,add_ssh_password,add_ssh_user)
    shell_cmd.cmd(add_password)
    create_time = time.strftime('%Y-%m-%d %X', time.localtime())
    models.Ssh_user.objects.create(user=add_ssh_user, password=add_ssh_password, host=host_list_str,
                                   create_time=create_time)

    return HttpResponse(json.dumps({'msg':'success'}))


@auth
def del_ssh_user(request):
    if request.method == 'POST':
        ansible = Ansible()
        for del_ssh_list in request.POST.lists():
            for user in del_ssh_list[1]:
                user_host = models.Ssh_user.objects.filter(user=user).values('host')[0]['host']
                # 删除ssh账号
                ansible.del_user(host=user_host, username=user)
                models.Ssh_user.objects.filter(user=user).delete()

        return HttpResponse(json.dumps({'msg':'success'}))


@auth
def update_ssh_user(request,*args,**kwargs):
    username = request.session.get('user')
    if request.method == 'GET':
        user_id = int(request.path.split('/')[-2])
        user_obj = models.Ssh_user.objects.filter(id=user_id)
        have_host = user_obj.values('host')[0]['host']
        user = user_obj.values('user')[0]['user']
        print(have_host,user)
        have_host_list1 = have_host.split(',')
        have_host_list = []
        for i in have_host_list1:
            if i:
                have_host_list.append(i)
        host_server = models.Linux_server.objects.values('server_name')
        not_host = []
        for i in host_server.values():
            not_host.append(i['server_name'])
        for host in have_host_list:
            if host in not_host:
                not_host.remove(host)
        return render(request, 'update_ssh_user.html',{'user': user, 'have_host_list': have_host_list, 'not_host': not_host, 'username': username})


@auth
def update_ssh_password_user(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        password = request.POST.get('password').strip()
        if password:
            models.Ssh_user.objects.filter(user=user).update(password=password)
            host = models.Ssh_user.objects.filter(user=user).values('host')[0]['host']
            shell_cmd = Shell()
            update_password = 'ansible %s -m shell -a \"echo \'%s\'|passwd --stdin %s \" ' % (host, password, user)
            shell_cmd.cmd(update_password)
            return HttpResponse(json.dumps({'msg': 'success'}))

        else:
            return HttpResponse('error')


@auth
def add_ssh_host(request):
    if request.method == 'GET':
        user = request.GET.get('user')
        add_host = request.GET.get('add_host')
        print(user,add_host)
        password = models.Ssh_user.objects.filter(user=user).values('password')[0]['password']
        print(password,add_host)
        user_obj = models.Ssh_user.objects.filter(user=user)
        old_host = user_obj.values('host')[0]['host']
        user_id = user_obj.values('id')[0]['id']
        if old_host:
            new_host = old_host + ',' + add_host
        else:
            new_host = add_host
        ansible = Ansible()
        ansible.add_user(host=add_host, username=user, password=password)
        update_password = 'ansible %s -m shell -a \"echo \'%s\'|passwd --stdin %s \" ' % (add_host, password, user) 
        h = models.Ssh_user.objects.filter(user=user).update(host=new_host)
        return redirect('/ssh_user/edit/%s/' % user_id)


@auth
def remove_ssh_host(request,*args,**kwargs):
    if request.method == 'GET':
        user = request.GET.get('user')
        remove_host = request.GET.get('remove_host')
        print(user,remove_host)
        user_obj = models.Ssh_user.objects.filter(user=user)
        old_host = user_obj.values('host')[0]['host']
        user_id = user_obj.values('id')[0]['id']
        new_host_list = old_host.split(',')
        new_host_list.remove(remove_host)
        new_host_str = ''
        for i in new_host_list:
            if i:
                new_host_str = new_host_str + ',' + i
        new_host = new_host_str.strip(',')
        ansible = Ansible()
        ansible.del_user(host=remove_host, username=user)
        h = models.Ssh_user.objects.filter(user=user).update(host=new_host)
        return redirect('/ssh_user/edit/%s/' % user_id)



def page_not_found(request):
    return render(request, '404.html')


@auth
def create_password(request):
    from ManageOps.src import create_random_str
    random_pass = create_random_str.random_str()
    return HttpResponse(random_pass)


@auth
def permission(request):
    #列出角色组及其成员
    username = request.session.get('user')
    permission_dict = {}
    roles_id_list = rbac_models.Role.objects.all()
    for id in roles_id_list:
        user_list = rbac_models.Role.objects.get(id=id.id).userinfo_set.all()
        roles_user = ''
        for user in user_list:
            if roles_user:
                roles_user = roles_user+' '+str(user.username)
            else:
                roles_user = str(user.username)
        permission_dict[id.title] = roles_user
    return render(request,'permission.html',{'permission_dict':permission_dict,'username':username})

@auth
def permission_edit_roles(request,*args,**kwargs):
    from django.db.models import Count
    role_id = int(request.path.split('/')[-2])
    roles_title = rbac_models.Role.objects.filter(id=role_id).values('title')[0]['title']
    username = request.session.get('user')
    #分组查询
    #所有权限的字典
    all_permission_dict = {}
    all_permission = rbac_models.Permission.objects.all()
    for index in range(len(all_permission.values("id"))):
        try:
            if all_permission_dict[all_permission.values("codes")[index]["codes"]]:
                all_permission_dict[all_permission.values("codes")[index]["codes"]][
                    all_permission.values("id")[index]['id']] = all_permission.values("title")[index]['title']
            else:
                all_permission_dict[all_permission.values("codes")[index]["codes"]] = {}
        except Exception as e:
            all_permission_dict[all_permission.values("codes")[index]["codes"]] = {}
        all_permission_dict[all_permission.values("codes")[index]["codes"]][all_permission.values("id")[index]['id']] = all_permission.values("title")[index]['title']

    all_codes = rbac_models.Permission.objects.values('codes').annotate(authorNum=Count("codes"))
    #当前权限的id列表
    # old_roles_permission = rbac_models.Role.objects.filter(title='admin').first()
    #反向查询角色拥有的权限id
    old_roles_permission = rbac_models.Role.objects.all().filter(id=role_id).values("permissions__id")

    old_roles_permission_id_list = []
    for i in old_roles_permission:
        old_roles_permission_id_list.append(i['permissions__id'])
    # for i in all_codes:
    #     code = rbac_models.Permission.objects.filter(codes=i['codes']).values('id')
    #     for id in code:
    #         old_roles_permission_id.append(id['id'])
    # print(old_roles_permission_id)

    #get列出某个角色的权限
    #post更改数据库权限（更改角色组权限）
    return render(request,'roles_permission.html',{'username':username,'all_permission_dict':all_permission_dict,'roles_id':role_id,'old_roles_permission_id_list':old_roles_permission_id_list})

@auth
def add_roles_group(request):
    if request.method == 'GET':
        return redirect('/403.html')
    if request.method == 'POST':
        roles = request.POST.get('add_roles')
        if auth_character(roles):
            return HttpResponse('非法字符')
        role_group = rbac_models.Role.objects.create(title=roles)
        if role_group:
            return HttpResponse(json.dumps({"msg":"success"}))
        return HttpResponse('error')

@auth
def delete_roles_group(request):
    if request.method == 'GET':
        return redirect('/403.html')
    if request.method == 'POST':
        #不允许删除的角色组
        protection_role_list = ['管理员','default']
        del_roles_list = request.POST.lists()
        default_id = rbac_models.Role.objects.filter(title='default').values('id')[0]['id']
        for i in del_roles_list:
            del_roles_list = i[1]
        for role in del_roles_list:
            if role in protection_role_list:
                continue
            user_list = rbac_models.Role.objects.get(title=role).userinfo_set.all()
            for user in user_list:
            #修改第三张表
                obj = rbac_models.UserInfo.objects.filter(name=str(user)).first().roles.set(str(default_id))
            # 删除角色
            del_role = rbac_models.Role.objects.filter(title=role).delete()

        return HttpResponse(json.dumps({"msg": "success"}))
    return HttpResponse('error')

@auth
def permission_update_roles(request):
    permission = request.POST.lists()
    roles_id = request.POST.get('roles')
    permission_list = []
    for i in permission:
        permission_list.append(i[1])
    permission_list = permission_list[0]
    #修改第三张表
    obj = rbac_models.Role.objects.filter(id=roles_id).first()
    #清空第三张表
    obj.permissions.clear()
    #添加数据到第三张表
    obj.permissions.add(*permission_list)
    if obj:
        return HttpResponse('1')
    else:
        return HttpResponse({'msg':'error'})


@auth
def server(request):
    username = request.session.get('user')
    current_page = request.GET.get('p', 1)
    current_page = int(current_page)
    server_count = models.Linux_server.objects.all().count()
    obj = page.PagerHelper(server_count, current_page, '/server/', 10)
    pager = obj.pager_str()
    server_list = models.Linux_server.objects.all()[obj.db_start:obj.db_end]
    last_integer = server_count //10
    last_remainder = server_count % 10
    if last_integer < 1:
        last_page = 1
    else:
        if last_remainder == 0:
            last_page = last_integer
        else:
            last_page = last_integer + 1

    return render(request,'server.html',{'username':username,'pager': mark_safe(pager),'last_page': last_page,'server_list':server_list})

@auth
def server_add(request):
    if request.method == 'GET':
        return redirect('/404.html')
    if request.method == 'POST':
        add_server = request.POST.get('add_server')
        auth_server = auth_character(add_server)
        if auth_server:
            return HttpResponse('非法字符')
        else:
            server = models.Linux_server.objects.create(server_name=add_server)
            if server:
                return HttpResponse(json.dumps({"msg": "success"}))
            else:
                return HttpResponse({'msg':'error'})

@auth
def server_delete(request):
    if request.method == 'GET':
        return redirect('/404.html')
    if request.method == 'POST':
        for i in request.POST.lists():
            del_server_list = i[1]
        for server in del_server_list:
            models.Linux_server.objects.filter(server_name=server).delete()
        return HttpResponse(json.dumps({"msg": "success"}))
