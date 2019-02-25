"""OpsManage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import handler404
from ManageOps import views



urlpatterns = [
#    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('login/', views.Login.as_view()),
    path('logout/', views.logout),
    path('git_code/', views.git_code),
    path('git_code/add_web/',views.add_web),
    path('git_code/delete_web/', views.delete_web),
    path('git_code/version_retreat/', views.version_retreat),
    path('git_code/update_new_www/', views.update_new_www),
    re_path("git_code/edit/([a-zA-Z0-9_\.]+)/", views.sites_statu),
    path('git_timing/', views.git_timing),
    path('git_timing/add/', views.add_cron),
    path('git_timing/delete/', views.delete_cron),
    path('change_password/', views.change_password),
    path('user_info/', views.user_info),
    path('user_info/add/', views.add_user),
    path('user_info/delete/', views.del_user),
    re_path('user_info/edit/(\d+)/',views.edit_user),
    path('user_info/update/', views.update_user),
    path('403.html', views.ban),

    path('update_email/', views.update_email),
    path('ssh_user/', views.ssh_user),
    path('ssh_user/add/', views.add_ssh_user),
    path('ssh_user/delete/', views.del_ssh_user),
    re_path('ssh_user/edit/(\d+)/', views.update_ssh_user),
    path('ssh_user/add_host/', views.add_ssh_host),
    path('ssh_user/remove_host/', views.remove_ssh_host),

    path('update_ssh_password_user', views.update_ssh_password_user),
    path('404.html',views.page_not_found),
    path('create_password',views.create_password),

    path('permission/',views.permission),
    re_path('permission/edit/(\d+)/',views.permission_edit_roles),
    path('permission/add_roles/',views.add_roles_group),
    path('permission/delete_roles/',views.delete_roles_group),
    path('permission/edit/update/',views.permission_update_roles),
    path('server/',views.server),
    path('server/add/',views.server_add),
    path('server/delete/',views.server_delete),

]
