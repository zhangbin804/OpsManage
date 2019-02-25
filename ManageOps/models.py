from django.db import models

#class Admin(models.Model):
#    username = models.CharField(max_length=32)
#    password = models.CharField(max_length=32)


class Code_version(models.Model):
    www_name = models.CharField(max_length=32,unique=True)
    www_dir = models.CharField(max_length=64)
    old_server_version = models.CharField(max_length=32)


#class Competence(models.Model):
#    that_power = models.IntegerField(default=0,unique=True)




#class User(models.Model):
#    username = models.CharField(max_length=32,unique=True,blank=False,null=False)
#    password = models.CharField(max_length=32,unique=False,blank=False,null=False)
#    email = models.EmailField(max_length=128,unique=True,blank=True,null=True)
#    competence = models.ForeignKey("Competence",to_field='that_power',on_delete=models.CASCADE,default=0)

class Linux_server(models.Model):
    server_name = models.CharField(max_length=32,unique=True,null=False)



class Ssh_user(models.Model):
    user = models.CharField(max_length=64,unique=True,null=False)
    password = models.CharField(max_length=32,unique=False,null=False)
    host = models.CharField(max_length=128,unique=False,null=False)
    competence = models.CharField(max_length=128,unique=False,null=True)
    create_time = models.CharField(max_length=32)

class Cron_git(models.Model):
    run_time = models.CharField(max_length=24,null=False)
    www_name = models.ForeignKey("Code_version",to_field='www_name',on_delete=models.CASCADE,default=0)
#    create_username = models.ForeignKey("UserInfo",to_field='name',on_delete=models.CASCADE,default=0)
    cron_shell_file_path = models.CharField(max_length=128)
    create_username = models.CharField(max_length=64,unique=True,null=False)
    create_time = models.CharField(max_length=24)
    atq_id = models.IntegerField(unique=True,null=False)
    
    class Meta:
        unique_together = ('www_name','run_time')
#    at_shell_filename = models.CharField(max_length=128,blank=True,null=True)
