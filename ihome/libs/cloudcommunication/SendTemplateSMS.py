from ihome.libs.cloudcommunication.CCPRestSDK import REST
from configparser import ConfigParser

# 主帐号
accountSid = '8aaf07086dcdca52016de121e81a0d94'

# 主帐号Token
accountToken = 'c5a599e8bcb94c16ae01348c0baab370'

# 应用Id
appId = '8aaf07086dcdca52016de121e86c0d9b'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id


class CCP():
    instancs = None

    def __new__(cls):
        """
        单例模式
        """
        if not cls.instancs:
            cls.instancs = super().__new__(cls)
        return cls.instancs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化REST SDK
        self.rest = REST(serverIP, serverPort, softVersion)
        self.rest.setAccount(accountSid, accountToken)
        self.rest.setAppId(appId)

    def send_template_sms(self, to, datas, temp_id):

        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        print(result)
        # print(result)
        # for k, v in result.items():

        #     if k == 'templateSMS':
        #         for k, s in v.items():
        #             print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))
        status = result.get('statusCode')
        return 0 if '000000' == status else -1


# sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == "__main__":
    ccp = CCP()
    ccp.send_template_sms('18855164785', ['12321', '5'], 1)
