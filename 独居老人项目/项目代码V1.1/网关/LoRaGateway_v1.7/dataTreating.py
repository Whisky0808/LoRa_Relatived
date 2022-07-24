import serial
import time
import random
import stopit
import struct
from datetime import datetime
import RPi.GPIO as GPIO
import equipmentMessage as eM
from uploadData import UploadData

# s = 0x01 + struct.Struct('6s I 3f') + 0x04
# s.size = 24
# 6s = 'NEW', 'SENSOR', 'POLLON'


class DataTreating:
    """将接收到的数据分为 开始标志‘S’ + 数据类型 + 设备号 + 数据(温度，湿度, 压强等) + 结束标志‘E’"""
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)     # 选择的串口
        self.Information = {'num': '0', 'temperature': '0', 'Humidity': '0', 'Pressure': '0', 'isFall': 'False', 'isCrue': 'False'}       # 存放终端发送过来的数据
        self.data = ""              # 暂时存放终端发送的数据
        self.RX_Packet = b""            # 存放数据包
        self.M0 = 22
        self.M1 = 27
        self.start = time.time()
        self.timer = None
        # self.frames_size = eM.frames_size
        self.s = struct.Struct('6s I 3f ? ?')
        self.packet_size = self.s.size   # 一个数据包的字节长度
        self.upload_data = UploadData()
        self.LoRa_INIT()
        eM.mailList.clear()

    def closeSerial(self):
        """关闭串口"""
        if self.ser.isOpen():
            self.ser.close()

    def PartitioningData(self):
        """将数据分割"""
        # self.Information.clear()                    # 清空列表, 不需要
        self.Information['num'] = str(self.RX_Packet[1])       # 设备号
        self.Information['temperature'] = str(self.RX_Packet[2])     # 温度
        self.Information['Humidity'] = str(self.RX_Packet[3])        # 湿度
        self.Information['Pressure'] = str(self.RX_Packet[4])        # 压强
        self.Information['isFall'] = str(self.RX_Packet[5])
        self.Information['isCure'] = str(self.RX_Packet[6])

    @stopit.threading_timeoutable()
    def Delay_To_Skip(self, t):
        """握手超时2s跳过"""
        while True:
            e = self.ser.read(1)
            if e == eM.Receive[t]:
                print(e)
                return True

    def LoRa_INIT(self):
        """
        描述：初始化网关
        当M0、M1分别为低电平、高电平时进入配置模式
        当M0、M1都为低电平时进入传输模式
        :return:
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        if self.ser.isOpen():
            time.sleep(1)
            self.ser.write(eM.CFG_REG_Gateway)
        temp = 0
        while True:
            self.data = self.ser.read(12)
            temp += 1
            if self.data == eM.RET_REG_Gateway:
                GPIO.output(self.M1, GPIO.LOW)
                break
            elif temp >= 5:
                temp = 0
                self.ser.write(eM.CFG_REG_Gateway)
        self.ser.flushInput()
        print("Initialization successful")

    def Delay_to_Retransmission(self):
        pass

    def SendData(self, form, num, num1=0, num2=0, num3=0):
        """发送数据"""
        value = (form, num, num1, num2, num3)
        array = bytearray(self.s.pack(*value))
        packet = bytearray()
        packet.append(0x01)
        for i in range(24):
            if array[i] == 0x01 or array[i] == 0x04 or array[i] == 0x1B:
                packet.append(0x1B)
            packet.append(array[i])
        packet.append(0x04)
        print(value, end=' ')
        print(eM.address[num])
        packet = eM.address[num] + bytes(packet)
        self.ser.write(packet)

    def Handshake(self, address):
        """进行三次握手"""
        while True:
            self.ser.write(address)
            while True:
                if self.ser.inWaiting() > 0:
                    break
            time.sleep(random.uniform(0.1, 0.5))
            self.ReceiveData()
            if self.RX_Packet[0] == b'reply':
                break

    def serialNumInit(self):
        for key in eM.serialNumber.keys():
            eM.serialNumber[key] = False

    def poll(self):
        """网关轮询终端"""
        if eM.address:
            temp = 0
            self.first = True
            # 可以考虑采用广播的方式通知全部的终端结束主动上报
            for i in eM.address.keys():
                self.SendData(b'first1', i)
                time.sleep(random.uniform(0.2, 0.5))
            self.serialNumInit()
            while True:
                self.ReceiveData()
                self.Treat()
                if temp > 10:
                    if self.check(b'first1', self.first):
                        # print("first finish")
                        break
                    temp = 0
                    self.first = False
                temp += 1
                #    if sign > 5:
                 #       break
            for i in eM.address.keys():
                self.SendData(b'second', i)
                time.sleep(random.uniform(0.2, 0.5))
            self.serialNumInit()
            sign = 0
            temp = 0
            self.first = True
            while True:
                self.ReceiveData()
                self.Treat()
                if temp > 10:
                    if self.check(b'second', self.first):
                        # print("second finish")
                        break
                    temp = 0
                    sign += 1
                   # if sign > 5:
                    #    break
                self.first = False
                temp += 1

            for i in eM.address.keys():
                self.SendData(b'endsop', i)
                time.sleep(random.uniform(1, 2))
            self.serialNumInit()
            sign = 0
            temp = 0
            self.first = True
            while True:
                self.ReceiveData()
                self.Treat()
                temp += 1
                if temp > 10:
                    if self.check(b'endsop', self.first):
                        # print("end finish")
                        break
                    temp = 0
                    sign += 1
                #    if sign > 5:
                 #       break
                self.first = False
                temp += 1
        
        self.start = time.time()
        print("poll end")
    
    def check(self, form, first):
        if first is True:
            for key, value in eM.serialNumber.items():
                if value is False:
                    eM.mailList.append(key)
            # first = False
        else:
            for i in range(len(eM.mailList)):
                if eM.serialNumber[eM.mailList[i]] is True:
                    eM.mailList.remove(eM.mailList[i])
        if eM.mailList:     # 列表空为False, 否则为Truem
            temp = 0
            for i in range(len(eM.mailList)):
                self.SendData(form, eM.mailList[i])
                time.sleep(random.uniform(1, 2))
                # self.ser.write(eM.getEquipmentAddress(eM.mailList[i]))
                time.sleep(1)
            return False
        else:
            # print(eM.mailList)
            # sign = 0
            # while self.ser.inWaiting() > 0:
            #     self.ReceiveData()
            #     self.Treat()
            return True
        
    def ReceiveData(self):
        """
        描述：采用字节填充的方式进行数据包的接收，当接收到数据时，调用一次函数接收一个数据包
        变量：
        SOH-0x01:代表数据包的开始
        EOH-0X04:代表数据包的结束
        Esc-0x1B:填充的字节
        :return: None
        """
        while True:
            if self.ser.inWaiting() > 0:
                first = self.ser.read(1)
                if first != b'\x1B':
                    if first == b'\x01':
                        self.RX_Packet = b''
                    elif first == b'\x04':
                        break
                    else:
                        self.RX_Packet += first
                else:
                    first = self.ser.read(1)
                    self.RX_Packet += first
            else:
                break
        # 判断接收到的数据包的长度是否符合标准数据包的长度
        if self.RX_Packet.__sizeof__() - b''.__sizeof__() == self.packet_size:
            self.RX_Packet = self.s.unpack(self.RX_Packet)
            print(self.RX_Packet)

    def Treat(self):
        """
        描述：对接收到的数据包的不同类型进行不同的处理
        SENSOR:接收到的数据包为传感器数据
        POLLON:判断接收到的数据包为轮询开始
        NEW:接收到的数据包为新节点加入的信息
        ADDH_L:接收到的数据包为节点的高低地址
        :return:
        """
        if type(self.RX_Packet) == tuple:
            if self.RX_Packet[0] == b'SENSOR':
                pass
                #self.PartitioningData()
                #self.upload_data.getAPI(self.Information)
                #self.upload_data.http_put(self.Information)
            elif self.RX_Packet[0] == b'POLLON':
                eM.serialNumber[self.RX_Packet[1]] = True
            elif self.RX_Packet[0] == b'NEWPOI':
                temp = bytearray()
                temp.append(int(self.RX_Packet[2]))
                temp.append(int(self.RX_Packet[3]))
                temp.append(int(self.RX_Packet[4]))
                temp = bytes(temp)
                eM.serialNumber[self.RX_Packet[1]] = False
                eM.address[self.RX_Packet[1]] = temp
                self.SendData(b'retNEW', self.RX_Packet[1])
            self.RX_Packet = b''

    def MyTimer(self):
        """
        每隔20s进行一次轮询
        :return:
        """
        if time.time() - self.start > 20:
            self.poll()

    def getRssi(self):
        # 在每个无线数据后跟随一个RSSI强度字节
        CFG = b'\xC2\x06\x01\xC3'
        REG = b'\xC1\x06\x01\xC3'
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        if self.ser.isOpen():
            time.sleep(1)
            self.ser.write(eM.CFG)
        temp = 0
        while True:
            self.data = self.ser.read(4)
            temp += 1
            if self.data == eM.RET:
                GPIO.output(self.M1, GPIO.LOW)
                break
            elif temp >= 5:
                temp = 0
                self.ser.write(eM.CFG)
        self.ser.flushInput()
        print("Initialization successful")
        s = struct.Struct('I')
        while True:
            if self.ser.inWaiting() > 0:
                buf = self.ser.read(4)
                buf = s.unpack(buf)
                print(buf)
                rssi = self.ser.read(2)
                print(ord(rssi) - 256)
