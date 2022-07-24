import math
import random
import time
import RPi.GPIO as GPIO


Ck = [0, 0x12, 0x13, 0x14, 0x15, 0x16]
M = len(Ck) - 1       # 可用信道数
P = 3       # 大于M的最小素数P
r = 1       # [1, M]中的非零数r
i = 0       # [1, P]中的索引i
t = 0       # 时隙计数器
# ser = None
neighborList = []
num = 2


# def openSerial():
#     ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # 选择的串口
#     return ser


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


def JS_2(cl, ser):
    """两个用户情况下使用"""
    global M, P, t, r, i, neighborList, Ck
    P = getLargestPrime(M)
    r0 = getRandom(1, M)
    i0 = getRandom(1, P)
    t = 0
    sign = True    # 是否成功连接
    start = time.time()
    connectTime = {}
    while sign:
        n = t/(3*P)
        m = t/(3*M*P)
        r = ((r0+n-1) % M)+1
        i = ((i0+m-1) % P)+1
        c = JSHopping(M, P, r, i, t)
        t = t+1
        # 修改信道
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
        time.sleep(random.uniform(1, 2))
        buf = cl.ReceiveData()
        if buf[0] == b'NEWPOI':
            if buf[4] not in neighborList:
                neighborList.append(buf[4])
                Ck.remove(buf[4])
                M = len(Ck) - 1
                connectTime[buf[4]] = time.time() - start
            cl.SendData(b'retNEW', buf[1])
            if len(neighborList) == 5:
                sign = False
                with open("time.txt", mode='a') as f:
                    f.write(str(connectTime) + '\n')
                    f.write("共用时:" + str(time.time() - start) + '\n')


def JS_K(ser):
    """多个用户情况下使用"""
    global M, P, t, r, i, neighborList
    P = getLargestPrime(M)
    r0 = getRandom(1, M)
    i0 = getRandom(1, P)
    t = 0
    # 是否成功连接
    sign = True
    start = time.time()
    while sign:
        while time.time() - start > 200*P:
            n = t / (3 * P)
            m = t / (3 * M * P)
            r = ((r0 + n - 1) % M) + 1
            i = ((i0 + m - 1) % P) + 1
            c = JSHopping(M, P, r, i, t)
            t = t + 1
            ch = Ck[c].to_bytes(1, byteorder='big', signed=False)

            ser.write(b'\xC2\x06\x01' + ch)
        start = time.time()
        while time.time() - start > 400*P:
            packed = Ck[c].to_bytes(1, byteorder='big', signed=False) + b'\x01'
            ser.write(packed)
            time.sleep(2)
            # ser.write(b'\x00\x00\x12\x01')
            if ser.read(4) == b'\x00\x00\x12\x01':
                neighborList.append(Ck[c])
                print(666)
                sign = False


def send():
    ser.write(b'\x00\x00\x12\x0f')


def readPack():
    global ser
    time.sleep(2)
    a = ser.read(4)
    print(a)

#
# if __name__ == '__main__':
#     ser = openSerial()
#     JS_2()
#     while True:
#         send()
#         readPack()
