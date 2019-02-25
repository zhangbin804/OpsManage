from aliyunsdkcore import client
from aliyunsdkslb.request.v20140515 import SetBackendServersRequest
from django.conf import settings


def slb_weight(ecs_id,weight=100):
    '''AccessKeyId、AccessKeySecret、Endpoint需自己添加'''
    AccessKeyId = 'xxxxxxxxxxxxxxx'
    AccessKeySecret = 'xxxxxxxxxxxxx'
    Endpoint = 'xxxxxxxxxxx'
    clien = client.AcsClient(AccessKeyId,AccessKeySecret,Endpoint)
    #ecs实例
    ecsA = ecs_id
    #权重
    ecsA_weight = weight
    req_parm1 = "BackendServers"
    req_parm2 = [{"ServerId": ecsA, "Weight": ecsA_weight}]
    request = SetBackendServersRequest.SetBackendServersRequest()
    request.set_accept_format('json')
    request.add_query_param('LoadBalancerId',settings.SLB_ID)
    request.add_query_param(req_parm1,req_parm2)
    response = clien.do_action_with_exception(request)
    print (response)  # 打印返回

