import datetime
from huawei import VRP_8

# 使用设备名称、告警类型、告警描述四个字段得到一个HTML版本的邮件主体
def create_mail_body(device_name, alert_type, alert_description):
    now_time = str(datetime.datetime.now()).split('.')[0]
    with open('template/head.html', encoding='utf-8') as f:
        text_head = f.read()
    with open('template/body.html', encoding='utf-8') as f:
        text_body = f.read()
    body = text_head + "\n" + text_body.format(device_name, alert_type, alert_description, now_time)
    return body


def huawei_runner():
    device_name = 'HuaweiVRP8'
    vrp_8 = VRP_8()

    # Task1. 获取信息生成JSON数据
    huawei_data = {}
    huawei_data['config'] = vrp_8.get_config()
    huawei_data['interfaces'] = vrp_8.get_interfaces()
    huawei_data['routeTable'] = vrp_8.get_route()
    huawei_data['monitor'] = {'cpu': vrp_8.monitor()}

    # Task2. 接口恢复与检查
    for interface in huawei_data['interfaces']:
        if interface['status'] != 'up':
            # 制作邮件主体并发送告警
            alert_des = f'{device_name} 的接口 {interface['name']} 被关闭了'
            body = create_mail_body(device_name, 'Error', alert_des)
            vrp_8.send_mail(subject='设备接口故障', body=body)

            # 开始接口恢复
            vrp_8.recover_interface(interface['name'])
            huawei_data['interfaces'] = vrp_8.get_interfaces()
            print("接口已恢复")

    # Task3. 配置新路由
    dst = '172.16.10.0'
    mask = '255.255.255.0'
    next = '10.1.1.10'
    if dst not in huawei_data['routeTable']:
        vrp_8.post_route(dst, mask, next)
        huawei_data['routeTable'] = vrp_8.get_route()
        print(f'新增了一条路由指向 {dst}，数据已更新')

    # Task4. 生成JSON
    vrp_8.to_json(huawei_data, 'data/cisco.json')

    vrp_8.device.disconnect()

if __name__ == "__main__":
    huawei_runner()