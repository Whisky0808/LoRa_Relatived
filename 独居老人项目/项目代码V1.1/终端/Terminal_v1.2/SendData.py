#!/usr/bin/python
# -*- coding:utf-8 -*-
# 终端运行程序，发送温度，速度，压强
import time
import serial
import RPi.GPIO as GPIO
import random
import struct
import BlindToMeet
# from tkinter import *
# sense hat 
# from sense_hat import SenseHat

from fall import Fall
from types import MethodType


ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # 记得改
ser.flushInput()
CFG_REG_Terminal = b'\xC2\x00\x09\x00\x00\x00\x62\x00\x12\x43\x00\x00'
RET_REG_Terminal = b'\xC1\x00\x09\x00\x00\x00\x62\x00\x12\x43\x00\x00'
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
    # ser.write(b'\xC2\x05\x02\x12\x43')  # 设置信道为0x12，定点传输
    time.sleep(random.uniform(1, 2))
    temp = 0
    while True:
        r_buff = ser.read(12)
        temp += 1
        if r_buff == RET_REG_Terminal:
            GPIO.output(M1, GPIO.LOW)
            print("Initialization successful")
            address = BlindToMeet.JS_2(ser)
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


def SendPacket(form, num, num1, num2, num3, isfall, isCure, add=None):
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
        #if temp > 2:
         #   break
        # temp += 1
        buf = b''
        # time.sleep(random.uniform(1, 2))


def toSendRssi():
    i = 0
    s = struct.Struct('I')
    while True:
        value = (i,)
        packet = b'\x00\x00\x11' + s.pack(*value)
        ser.write(packet)
        i += 1


if __name__ == '__main__':
    init()
    sense = SenseHat()

    isfall = False
    isCure = False
    x = [225, 0, 0]  # Red
    question_mark = [
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x,
        x, x, x, x, x, x, x, x
    ]
    def direction_fall():
        global isfall
        isfall = True
        sense.set_pixels(question_mark)


    def press_button():
        global isCure
        isCure = True

    my_fall = Fall()
    # 替换跌倒响应函数
    my_fall.direction_fall = MethodType(direction_fall, my_fall)
    my_fall.press_button = MethodType(press_button, my_fall)

    # 启动
    my_fall.start()

    while True:
        buff = ser.inWaiting()
        if buff > 0:
            time.sleep(random.uniform(0.5, 0.7))
            ReceivedPollingMessage()
            print("poll end")
        else:
            time.sleep(random.uniform(2, 3))
            # PRESS_DATA = sense.get_pressure()
            # TEMP_DATA = sense.get_temperature()
            # Hum = sense.get_humidity()
            PRESS_DATA = random.uniform(1000, 1500)
            TEMP_DATA = random.uniform(10, 15)
            Hum = random.uniform(50, 70)
            SendPacket(b'SENSOR', 1, TEMP_DATA, Hum, PRESS_DATA, isfall, isCure)
            isfall = False
            isCure = False