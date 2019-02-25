from django import template
from django.utils.safestring import mark_safe
from rbac import models as rbac_models
register = template.Library()

#返回角色组名称
@register.simple_tag
def role_group(user):
    return user.roles.values("title")[0]["title"]

@register.simple_tag
def role_id(role_title):
    return rbac_models.Role.objects.filter(title=role_title).values('id')[0]['id']