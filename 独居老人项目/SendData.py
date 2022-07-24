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
from sense_hat import SenseHat

from fall import Fall
from types import MethodType


s = struct.Struct('6s I 3f ? ?')
M0 = 22
M1 = 27
address = b''
RX_Packet = b''
packet_size = s.size


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
    packet = add + bytes(packet)
    ser.write(packet)
    print(value)


def ReceiveData():
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
    if RX_Packet.__sizeof__() - b''.__sizeof__() == packet_size:
        RX_Packet = s.unpack(RX_Packet)
        print(RX_Packet)
        return RX_Packet[0]
