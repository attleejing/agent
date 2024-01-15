from connection import Net


class VRP_8(Net):
    def __init__(self):
        super().__init__('huawei_vrpv8', '30.61.6.222', 'huaweiuser', 'Huawei123@')

    # 获取配置
    ## 输出字符串形式的设备配置
    def get_config(self):
        cmd = 'display current-configuration'
        info = self.device.send_command(cmd)
        #data_str = info.split('sysname HUAWEI\n!')[1]
        data_str = ''.join(info.split('#')[1:])
        return data_str

    # 获取接口
    ## 输出列表形式的接口数据
    def get_interfaces(self):
        cmd = 'display ip interface brief'
        info = self.device.send_command(cmd)
        data_list = []
        for line in ''.join(info.split('VPN')[1:]).split('\n')[1:-1]:
            if_name = line.split()[0]
            if_ip = line.split()[1]
            status = line.split()[3]
            data_list.append({'name': if_name,
                              'ip': if_ip,
                              'status': status})
        return data_list

    # 接口恢复UP  
    def recover_interface(self, if_name):
        self.reconnect()
        cmd_list = [f'interface {if_name}', 'undo shutdown']
        self.device.send_config_set(cmd_list)
        self.device.commit()

    # 获取路由表
    ## 输出字符串形式的设备路由表信息
    def get_route(self):
        cmd = 'display ip routing-table'
        info = self.device.send_command(cmd)
        data_str = '\n'.join([line for line in info.split('\n') if '/' in line])
         #  data_str = info.split('\n\n')[2].strip()
        return data_str

    # 新增路由条目
    def post_route(self, dst_n, mask, next):
        self.reconnect()
        cmd_list = [f'ip route {dst_n} {mask} {next}']
        self.device.send_config_set(cmd_list)
        self.device.commit()

    # 自动化巡检
    ## 输出字典形式的CPU使用率数据
    def monitor(self):
        data_dict = {}
        cpu_cmd = 'display cpu'
        cpu_info = self.device.send_command(cpu_cmd)
        cpu_list = [line for line in cpu_info.split('\n') if 'cpu' in line]
        for line in cpu_list:
            cpu_name, current, cpu_5s, cpu_1m, cpu_5m = line.split()[:5]
            data_dict[cpu_name] = {'cpu_current': current,
                                   'cpu_5sec': cpu_5s,
                                   'cpu_1min': cpu_1m,
                                   'cpu_5min': cpu_5m}
        return data_dict