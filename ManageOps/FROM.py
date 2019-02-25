from django import forms

class NewPassword(forms.Form):
    old_password = forms.CharField(min_length=6, max_length=32,
                                   error_messages={'required': '密码不能为空', 'min_length': '密码长度不能小于6',
                                                   'max_length': '密码长度不能大于32', })
    new_password = forms.CharField(min_length=6, max_length=32,
                                   error_messages={'required': '密码不能为空', 'min_length': '密码长度不能小于6',
                                                   'max_length': '密码长度不能大于32', })
    new_password2 = forms.CharField(min_length=6, max_length=32,
                                    error_messages={'required': '密码不能为空', 'min_length': '密码长度不能小于6',
                                                    'max_length': '密码长度不能大于32', })
