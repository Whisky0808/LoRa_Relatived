
List = {
        '1': {
            'APIKEY': 'sSEfNI52BkIrwjp5SWfGb4WCEfk=',
            'apiurl': 'http://api.heclouds.com/devices/611378846/datapoints'
        },
        '2': {
            'APIKEY': 'OcKbYsVqRzY0YmZ5=SyXUkXtF5I=',
            'apiurl': 'http://api.heclouds.com/devices/642498913/datapoints'
        },
        '3': {
            'APIKEY': 'nN3hG5BMYZaTbnqAxwTqZ6PLqhs=',
            'apiurl': 'http://api.heclouds.com/devices/642500518/datapoints'
        },
        '4': {
            'APIKEY': '7HM214lMHeL3l1pCHIUkE0iPQvM=',
            'apiurl': 'http://api.heclouds.com/devices/645647371/datapoints'
        }
}

dictionaries = {'APIKEY': '0', 'apiurl': '0'}

CFG_REG_Gateway = b'\xC2\x00\x09\xFF\xFF\x00\x62\x00\x11\x43\x00\x00'         # 网关寄存器配置,设置为定点传输
RET_REG_Gateway = b'\xC1\x00\x09\xFF\xFF\x00\x62\x00\x11\x43\x00\x00'

Receive = ["send_1 receive",
           "send_2 receive"]

serialNumber = {
    # 1: False
 #   2: False
}       # 终端名单

# 设备号：b'高地址，低地址，信道'
address = {
    # 1: b'\x00\x02\x12',
    # 2: b'\x00\x01\x15'
}       # 终端的地址

mailList = []       # 未进入轮询的名单

equipmentNum = 2        # 终端数量

packet_size = 24   # 元组数据字节数


def get_API_Information(information):
    dictionaries['APIKEY'] = List[str(information['num'])]['APIKEY']
    dictionaries['apiurl'] = List[str(information['num'])]['apiurl']
    # dictionaries['datakind'] = datakind[information[1]]
    return dictionaries


def getEquipmentAddress(i):
    return address[i]
