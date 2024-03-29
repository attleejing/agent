import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from netmiko import ConnectHandler

# 这里可以注册一个TOM邮箱或者自己可用SMTP的邮箱，使用自己的账户信息替代下面的内容
usermail = "attleejing@tom.com"
password = "12345678Tencent"
smtpserver = "smtp.tom.com"
smtpport = 25

# 这里可以使用另一个邮箱来接收邮件
alert_mail = "attlee6521@hotmail.com"


# Net底层类
class Net:
    # Basic ssh connect & json data output(file save)
    def __init__(self, device_type, host, username, password):
        self.device_info = {
            "device_type": device_type,
            "ip" : host, 
            "port" : 22, 
            "username" : username,
            "password" : password,
        }
        self.device = self.connect()

    # 基本连接功能
    def connect(self):
        return ConnectHandler(**self.device_info)
    
    # 断线重连功能
    def reconnect(self):
        self.device.disconnect()
        self.device = self.connect()
    
    # 数据输出为JSON
    def to_json(self, data_dict, file_path):
        with open(file_path, 'w') as f:
            # 写文件创建日志
            json.dump(data_dict, fp=f, indent=4)

    # 发送邮件功能
    def send_mail(self, subject, body):
        message = MIMEText(body, 'html', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = usermail
        message['To'] = alert_mail
        sender = smtplib.SMTP(smtpserver, smtpport)
        sender.login(usermail, password)
        sender.sendmail(usermail, alert_mail, message.as_string())
        sender.quit()