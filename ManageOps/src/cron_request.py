#/usr/bin/python3
import requests
import sys,re
import os

username = sys.argv[1]
password = sys.argv[2]
www_name = sys.argv[3]
bash_file = sys.argv[4]
PATH_URL = sys.argv[5]
print(bash_file)

with open(bash_file,'r',encoding='utf-8') as f:
    text = f.read()
#    print(text)
    cron_id = re.findall('cron_id=[0-9]+',text)[0]
    cron_id = cron_id.replace('cron_id=','')
    print(cron_id)

new_www_code_url = PATH_URL+'/git_code/update_new_www/'
url = PATH_URL+'/login/'
delete_cron_url = PATH_URL+'/git_timing/delete/'

session = requests.Session()
data = {
    'user':username,
    'password':password
}
update_data = {
'www_name':www_name
}

delete_data = {
'del_cron_list':[cron_id]
}

def post_url(url,data,new_www_code_url,update_data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',

        }
    response = session.post(url,data=data)
#    login = session.get('http://127.0.0.1:8000/index/')
    update_code = session.post(new_www_code_url,data=update_data)
    delete_cron = session.post(delete_cron_url,data=delete_data)
    print('-'*100)



if __name__ == '__main__':
    post_url(url,data,new_www_code_url,update_data)
#    os.remove(bash_file)

