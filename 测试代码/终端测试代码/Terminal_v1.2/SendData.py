#!/usr/bin/python
# -*- coding:utf-8 -*-
# 终端运行程序，发送温度，速度，压强
import time
import serial
import RPi.GPIO as GPIO
import random
import struct
import BlindToMeet

from types import MethodType


ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)  # 记得改
ser.flushInput()
deviceID = 1
channel = deviceID
CFG_REG_Terminal = b'\xC2\x00\x09\x00\x00\x00\x62\x00' + channel.to_bytes(1, byteorder='big', signed=False) + b'\x43\x00\x00'
RET_REG_Terminal = b'\xC1\x00\x09\x00\x00\x00\x62\x00' + channel.to_bytes(1, byteorder='big', signed=False) + b'\x43\x00\x00'
s = struct.Struct('6s I 3f ? ?')
M0 = 22
M1 = 27
PRESS_DATA = 0.0
TEMP_DATA = 0.0
address = b''
RX_Packet = b''
packet_size = s.size


def init():
    global address
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(M0, GPIO.OUT)
    GPIO.setup(M1, GPIO.OUT)

    GPIO.output(M0, GPIO.LOW)
    GPIO.output(M1, GPIO.HIGH)
    ser.write(CFG_REG_Terminal)
    time.sleep(random.uniform(1, 2))
    temp = 0
    while True:
        r_buff = ser.read(12)
        temp += 1
        if r_buff == RET_REG_Terminal:
            GPIO.output(M1, GPIO.LOW)
            print("Initialization successful")
            address = BlindToMeet.JS_2(ser, channel, deviceID)
            # address = b'\xFF\xFF\x11'
            print("find successful")
            break
        elif temp >= 5:
            temp = 0
            ser.write(CFG_REG_Terminal)
    ser.flushInput()


# s = 'S' + struct.Struct('6s I 3f') + 'E'
# 6s = 'NEW', 'SENSOR', 'POLLON'
# ('POLLON', 2, 6, 66, 666)


def SendPacket(form, num, num1, num2, num3, add=None, isfall=False, isCure=False):
    global address
    value = (form, num, num1, num2, num3, isfall, isCure)
    array = bytearray(s.pack(*value))
    packet = bytearray()
    packet.append(0x01)
    for i in range(packet_size):
        if array[i] == 0x01 or array[i] == 0x04 or array[i] == 0x1B:
            packet.append(0x1B)
        packet.append(array[i])
    packet.append(0x04)
    if add is None:
        packet = address + bytes(packet)
    else:
        packet = add + bytes(packet)
        address = add
    ser.write(packet)
    print(value)


def ReceiveData():
    """
    描述：采用字节填充的方式进行数据包的接收，当接收到数据时，调用一次函数接收一个数据包
    变量：
    SOH-0x01:代表数据包的开始
    EOH-0X04:代表数据包的结束
    Esc-0x1B:填充的字节
    :return: 
    """
    global RX_Packet
    RX_Packet = b''
    while True:
        if ser.inWaiting() > 0:
            first = ser.read(1)
            if first != b'\x1B':
                if first == b'\x01':
                    RX_Packet = b''
                elif first == b'\x04':
                    break
                else:
                    RX_Packet += first
            else:
                first = ser.read(1)
                RX_Packet += first
        else:
            break
    # print(RX_Packet)
    # 判断接收到的数据包的长度是否符合标准数据包的长度
    #print(RX_Packet)
    if RX_Packet.__sizeof__() - b''.__sizeof__() == packet_size:
        RX_Packet = s.unpack(RX_Packet)
        print(RX_Packet)
        return RX_Packet[0]


def ReceivedPollingMessage():
    # \x00为轮询开始，\x01为轮询结束，\x10为轮询到自己
    temp = 0
    while True:
        # time.sleep(random.uniform(0.5, 0.7))
        buf = ReceiveData()
        if buf == b'first1':
            SendPacket(b'POLLON', 1, 2.1, 3.1, 4.1)
        elif buf == b'second':
            SendPacket(b'POLLON', 1, 6.1, 7.1, 8.1)
        elif buf == b'endsop':
            SendPacket(b'POLLON', 1, 0, 0, 0)
            print("end recived")
            # temp += 1
            break


if __name__ == '__main__':
    init()

    isfall = False
    isCure = False
    total = 50

    while total >= 0:
        PRESS_DATA = random.uniform(1000, 1500)
        TEMP_DATA = random.uniform(10, 15)
        Hum = random.uniform(50, 70)
        SendPacket(b'SENSOR', deviceID, TEMP_DATA, Hum, PRESS_DATA, None, isfall, isCure)
        time.sleep(random.uniform(1, 2))
        total -= 1
    SendPacket(b'STOPTX', deviceID, 0，0，0，None, isfall, isCure)
   
