import os
import sys
import time
from datetime import datetime
import json



class Shell:

    def str_all(self,*args):
        file_all = ''
        for file in args[0]:
            file_all = file_all + file
        return file_all

    def shell(self,*args):
        os.system(self.str_all(args))
        return 1

    def cmd(self,*args):
        shell_cmd = os.popen(self.str_all(args)).read()
        return shell_cmd




class Git(Shell):

    def __init__(self,jobs_dir):
        self.jobs_dir = jobs_dir
        self.git_dir()

    def clone(self,clone_url='',branch='master',path='',clone_name=''):
        '''
        :param clone_url:  git仓库的地址
        :param branch:  分支名
        :param path:  指定clone的路径
        :param clone_name:  指定clone的名字（默认和仓库名一样）
        '''
        if clone_name == False:
            clone_name = clone_url.split('/')[-1].split('.')[-2]
        git_clone = 'git clone -b '+branch+' '+clone_url+' '+path+clone_name
        return self.shell(git_clone)

    def git_dir(self):
        '''
        :param dirname:  git的工作目录
        '''
        os.chdir(self.jobs_dir)
        return self.jobs_dir

    def add(self,*args):
        return self.cmd('git add '+self.str_all(args))

    def commit(self,*args):
        return self.cmd('git commit  -m  "{args}"'.format(args=self.__str_all(args)))

    def branch(self,parameter='',branch_name=''):
        '''
        :param parameter:  参数
        :param branch_name: 分支名
        '''
        return self.cmd('git branch {parameter} {branch_name}'.format(parameter='-'+parameter,branch_name=branch_name))

    def checkout(self,*args):
        return self.cmd('git checkout '+self.str_all(args))

    def tag(self,*args):
        return self.cmd('git tag '+self.str_all(args))

    def log(self,*args):
        return self.cmd('git log '+self.str_all(args))

    def deff(self,*args):
        return self.cmd('git diff' +self.str_all(args))

    def push(self,*args):
        return self.cmd('git push '+self.str_all(args))

    def pull(self,*args):
        return self.cmd('git pull '+self.str_all(args))

    def reset(self,commit_id):
        '''
        :param commit_id: 回退版本的id号
        '''
        return self.cmd('git reset --hard {commit_id}'.format(commit_id=commit_id))

    def status(self,*args):
        return self.cmd('git status '+self.str_all(args))

    def fetch(self):
        return self.cmd('git fetch')

    def master_versions(self,num=1):
        '''
        :param num: master分支上最新提交的记录条数
        '''
        version_str = self.log('origin/master -n {num}'.format(num=num))
        master_version_list = version_str.strip().split('\n')
        master_version = master_version_list[-1].strip()
        return master_version

    def old_versions(self,num=1):
        version_str = self.log(' -n {num}'.format(num=num))
        old_version_list = version_str.strip().split('\n')
        old_version = old_version_list[-1].strip()
        return old_version

    def git_log_version_10(self,num=11):
        version_list_cmd = self.cmd('git  log --oneline -n {num}'.format(num=num))
        return version_list_cmd


class Ansible(Shell):
    '''
    所有host参数都代表ip或模块
    '''

    def yum(self,host='',name='',state='present'):
        '''
        :param name:  yum下载的包名（如vim）
        :param state: 状态（present，absent，latest）
        '''
        yum_cmd = 'ansible {host} -m yum -a \'name={name} state={state}\'  '.format(host=host,name=name,state=state)
        return print(yum_cmd)

    def service(self,host='',service_name='',enabled='',state='start'):
        '''
        :param service_name: 服务名
        :param enabled: (yes|no) 是否开机自启
        :param state: （started,stopped,restarted,reloaded）
        '''
        service_cmd = 'ansible {host} -m service -a \'name={service_name} enabled={enabled} state={state}\' '.format(host=host,service_name=service_name,enabled=enabled,state=state)
        return print(service_cmd)
        pass

    def cp(self,host='',local_file='',dest_name=''):
        '''
        :param local_file: 本地需要copy的文件
        :param dest_name: 复制到其它服务器的路径或名字
        '''
        cp_cmd = 'ansible {host} -m copy -a \'src={local_file} dest={dest_name} \' '.format(host=host,local_file=local_file,dest_name=dest_name)
        return print(cp_cmd)

    def script(self,host='',script_path=''):
        '''
        :param script_path: 脚本的路径与名字
        '''
        script_cmd = 'ansible {host} -m script -a \'{script_path}\' '.format(host=host,script_path=script_path)
        return print(script_cmd)


    def add_cron(self,host='',cron_name='',minute='*',hour='*',day='*',month='*',weekday='*',cron_cmd=''):
        '''
        :param cron_name:  定时任务的名字
        :param minute:  分钟 0-59
        :param hour: 小时 1-12
        :param day: 天  1-31
        :param month: 月份 1-12
        :param weekday: 周  0-6
        :param cron_cmd: 执行的定时任务命令
        '''
        create_cron = 'ansible {host} -m cron -a \'name="{cron_name}", minute={minute} hour={hour} day={day} month={month} weekday={weekday} job="{cron_cmd}"\''.format(host=host,cron_name=cron_name,minute=minute,hour=hour,day=day,month=month,weekday=weekday,cron_cmd=cron_cmd)
        return print(create_cron)

    def del_cron(self,host='',cron_name=''):
        '''
        :param cron_name:  需要删除的定时任务名字
        '''
        delete_cron = 'ansible {host} -m cron -a \'name="{cron_name}", state=absent \' '.format(host=host,cron_name=cron_name)
        return print(delete_cron)

    def add_user(self,host='',username='',password='',home='',uid='',comment=''):
        '''
        :param username: 账号名
        :param password: 密码
        :param home: 指定的家目录
        :param uid: 指定的uid号
        :param comment: 介绍（注释）
        '''

        #passwd = os.popen('openssl passwd -salt -1 {password}'.format(password=password)).read().strip()
        passwd = os.popen("echo '{password}' | openssl passwd -1 -salt $(< /dev/urandom tr -dc '[:alnum:]' | head -c 32) -stdin".format(password=password)).read().strip()
        add_user_cmd = 'ansible {host} -m user -a \'name={username} password="{password}"\''.format(host=host,username=username,password=passwd)
        return self.cmd(add_user_cmd)


    def del_user(self,host='',username='',remove_home='yes'):
        del_user_cmd = 'ansible {host} -m user -a "name={username} state=absent remove={remove_home}" '.format(host=host,username=username,remove_home=remove_home)
        return self.cmd(del_user_cmd)
