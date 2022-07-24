import serial
import RPi.GPIO as GPIO
import math
import random
import time

M = 4  # 可用信道数
P = 5  # 大于M的最小素数P
r = 1  # [1, M]中的非零数r
i = 0  # [1, P]中的索引i
t = 0  # 时隙计数器
# Ck = [0, 0x13, 0x14, 0x15, 0x00]
Ck = [0, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]
ser = None
neighborList = []
num = 2
s = struct.Struct('6s I 3f I ?')
packet_size = s.size  # 一个数据包的字节长度
RX_Packet = b""
serialNumber = {
    # 1: False
    #   2: False
}  # 终端名单

# 设备号：b'高地址，低地址，信道'
address = {
    # 1: b'\x00\x02\x12',
    # 2: b'\x00\x01\x15'
}  # 终端的地址
timeList = []


def initParameter():
    global P, M
    M = len(Ck) - 1
    P = getLargestPrime(M)


def openSerial():
    global ser
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # 选择的串口


def initLoRa():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(22, GPIO.OUT)
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(22, GPIO.LOW)
    GPIO.output(27, GPIO.HIGH)

    # ser.write(b'\xC2\x06\x01\x40')
    ser.write(b'\xC2\x00\x09\x01\x01\x00\x62\x00\x00\x43\x00\x00')
    while True:
        buf = ser.read(4)
        # if buf == b'\xC1\x06\x01\x40':  # 设置为定点传输
        if buf == b'\xC1\x00\x09\x01\x01\x00\x62\x00\x00\x43\x00\x00':
            GPIO.output(27, GPIO.LOW)
            break
        else:
            # ser.write(b'\xC2\x06\x01\x40')
            ser.write(b'\xC2\x00\x09\x01\x01\x00\x62\x00\x00\x43\x00\x00')


def isPrime(num):
    """判断是否为质数"""
    if num < 2:
        return False
    k = 2
    s = math.sqrt(num)
    while k <= s:
        if num % k == 0:
            return False
        k += 1
    return True


def getLargestPrime(M):
    """得到一个大于M的最小素数"""
    k = M + 1
    while True:
        if isPrime(k):
            return k
        k += 1


def getRandom(lower, upper):
    """在lower~upper之间获取一个随机数"""
    random.seed(time.time())
    list1 = [10, 100, 1000, 10000, 100000, 1000000]
    k = int(random.random() * random.choice(list1))
    return lower + k % (upper - lower + 1)


def JSHopping(M, P, r, i, t):
    """获取时隙t时的跳频信道"""
    j = 0
    t %= (3 * P)
    if t < (2 * P):
        j = (i + (t * r) - 1) % P + 1
    else:
        j = r
    if j > M:
        j = (j - 1) % M + 1
    return j


def JS_2():
    """两个用户情况下使用"""
    global M, P, t, r, i, neighborList, ser
    P = getLargestPrime(M)
    r0 = getRandom(1, M)
    i0 = getRandom(1, P)
    t = 0
    sign = True  # 是否成功连接
    while sign:
        n = t / (3 * P)
        m = t / (3 * M * P)
        r = ((r0 + n - 1) % M) + 1
        i = ((i0 + m - 1) % P) + 1
        c = int(JSHopping(M, P, r, i, t))
        t = t + 1

        ch = Ck[c].to_bytes(1, byteorder='big', signed=False)
        GPIO.output(27, GPIO.HIGH)
        ser.write(b'\xC2\x05\x01' + ch)  # 设置信道
        while True:
            buf = ser.read(4)
            if buf == b'\xC1\x05\x01' + ch:
                GPIO.output(27, GPIO.LOW)
                break
            else:
                ser.write(b'\xC2\x05\x01' + ch)
        # packed = b'\x01\x01' + Ck[c].to_bytes(1, byteorder='big', signed=False)
        # ser.write(packed)
        # 高、低地址、信道
        # SendData.SendPacket(b'NEWPOI', deviceID, 0x00, 0x00, channel, packed)
        time.sleep(random.uniform(1, 2))
        buf = ReceiveData()
        if buf == b'retNEW':
            sign = False


def JS_K(ser):
    """个用户情况下使用"""
    global M, P, t, r, i, neighborList
    P = getLargestPrime(M)
    r0 = getRandom(1, M)
    i0 = getRandom(1, P)
    t = 0
    # 是否成功连接
    sign = True
    start = time.time()
    while sign:
        while time.time() - start > 200 * P:
            n = t / (3 * P)
            m = t / (3 * M * P)
            r = ((r0 + n - 1) % M) + 1
            i = ((i0 + m - 1) % P) + 1
            c = JSHopping(M, P, r, i, t)
            t = t + 1
            ch = Ck[c].to_bytes(1, byteorder='big', signed=False)

            ser.write(b'\xC2\x06\x01' + ch)
        start = time.time()
        while time.time() - start > 400 * P:
            packed = Ck[c].to_bytes(1, byteorder='big', signed=False) + b'\x01'
            ser.write(packed)
            time.sleep(2)
            # ser.write(b'\x00\x00\x12\x01')
            if ser.read(4) == b'\x00\x00\x12\x01':
                neighborList.append(Ck[c])
                print(666)
                sign = False


def ReceiveData():
    global ser, RX_Packet, packet_size
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
    # 判断接收到的数据包的长度是否符合标准数据包的长度
    if RX_Packet.__sizeof__() - b''.__sizeof__() == packet_size:
        RX_Packet = s.unpack(RX_Packet)
        Treat()
        print(RX_Packet)
        return RX_Packet[0]


def Treat():
    global RX_Packet, serialNumber, address
    if type(RX_Packet) == tuple:
        if RX_Packet[0] == b'NEWPOI':
            temp = bytearray()
            temp.append(int(RX_Packet[2]))
            temp.append(int(RX_Packet[3]))
            temp.append(int(RX_Packet[4]))
            temp = bytes(temp)
            serialNumber[RX_Packet[1]] = False
            address[RX_Packet[1]] = temp
            timeList.append(RX_Packet[5])
            SendData(b'retNEW', RX_Packet[1])
        elif RX_Packet[0] == b'STOPTX':
            print(timeList)
            with open("timeList.txt") as f:
                f.write(str(timeList) + '\n')
        RX_Packet = b''


def SendData(form, num, num1=0, num2=0, num3=0, isFall=0, isCure=False):
    """发送数据"""
    value = (form, num, num1, num2, num3, isFall, isCure)
    array = bytearray(s.pack(*value))
    packet = bytearray()
    packet.append(0x01)
    for i in range(packet_size):
        if array[i] == 0x01 or array[i] == 0x04 or array[i] == 0x1B:
            packet.append(0x1B)
        packet.append(array[i])
    packet.append(0x04)
    packet = address[num] + bytes(packet)
    ser.write(packet)


if __name__ == '__main__':
    initParameter()
    openSerial()
    initLoRa()
    total = 50
    while total > 0:
        JS_2()
        total -= 1

    GPIO.output(27, GPIO.HIGH)
    ser.write(b'\xC2\x05\x01\x01')  # 设置信道
    while True:
        buf = ser.read(4)
        if buf == b'\xC1\x05\x01\x01':
            GPIO.output(27, GPIO.LOW)
            break
        else:
            ser.write(b'\xC2\x05\x01\x01')
    while True:
        ReceiveData()
