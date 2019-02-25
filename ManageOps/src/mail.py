import smtplib
from email.mime.text import MIMEText


mailto_list = ['需发送邮箱的列表']
mail_host = "smtp.163.com"
mail_user = "邮箱账号"
mail_pass = "邮箱密码"

mail_news = {}

def send_mail(to_list, sub, content):
    me = "LogServer"+"<"+mail_user+">"
    msg = MIMEText(content, _subtype='plain', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(str(e))
        return False

class Mail:
    def __init__(self,mail_host="smtp.163.com",
                 mail_user="邮箱账号",mail_pass="邮箱密码"):

        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass

    def send_mail(self,to_list, sub, content):
        me = "LogServer" + "<" + mail_user + ">"
        msg = MIMEText(content, _subtype='plain', _charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)
        try:
            server = smtplib.SMTP()
            server.connect(self.mail_host)
            server.login(self.mail_user,self.mail_pass)
            server.sendmail(me, to_list, msg.as_string())
            server.close()
            return True
        except Exception as e:
            print(str(e))
            return False




