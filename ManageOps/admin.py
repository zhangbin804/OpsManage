from django.contrib import admin
from rbac import models
admin.site.register(models.Permission)
admin.site.register(models.Role)
admin.site.register(models.UserInfo)
admin.site.register(models.Group)
admin.site.register(models.Menu)

