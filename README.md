# git版本上线控制


# 介绍
主要是为了把上线流程交给开发

所以把上线与回滚全部实现web化管理



# 主要功能
## 1、版本控制

1、版本的上线(master上的最新版本)

2、版本的回滚(10个版本)

3、基于at实现的定时上线

4、上线与回滚钉钉提示

5、上线过程自动更改slb权重（暂时没用到，所以只写了控制slb权重的daemon）

阿里云slb程序文件ManageOps/src/aliyun_slb.py

## 2、ssh账号管理（基于ansible）

1、添加或删除ssh账号

2、随机生成密码的功能

## 3、服务器

1、服务器的添加与删除

## 4、使用RBAC控制权限

1、默认有admin账号，密码为123456

2、初始管理员（所有权限）和default（无任何权限）角色

## 5、仪表盘预留

1、可以根据需求自己写一些监控或其他


# 依赖安装

python版本为Python3.6

1、at安装

yum install at -y

2、安装python第三方库

pip3 install -r requirements.txt
