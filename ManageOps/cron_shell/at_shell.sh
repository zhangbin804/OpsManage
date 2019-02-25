#!/bin/bash 


user=$1
password=$2
www_name=$3
home_dir=$4
path_url=$5
cron_id=number

cron_request_file=${home_dir}/OpsManage/ManageOps/src/cron_request.py
shell_filename=${home_dir}/OpsManage/ManageOps/cron_shell/request_cron_`uuidgen |cut  -c27-`.sh
cat>>${shell_filename}<<EOF
python3 ${cron_request_file} ${user} ${password} ${www_name} ${shell_filename} ${path_url} cron_id=number
EOF


echo  -n ${shell_filename}
