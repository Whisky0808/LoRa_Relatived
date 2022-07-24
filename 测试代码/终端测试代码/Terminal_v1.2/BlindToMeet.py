import math
import random
import time
import SendData

M = 4       # 可用信道数
P = 5       # 大于M的最小素数P
r = 1       # [1, M]中的非零数r
i = 0       # [1, P]中的索引i
t = 0       # 时隙计数器
Ck = [0, 0x13, 0x14, 0x15, 0x00]
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


def JS_2(ser, channel, deviceID):
    """两个用户情况下使用"""
    global M, P, t, r, i, neighborList
    P = getLargestPrime(M)
    r0 = getRandom(1, M)
    i0 = getRandom(1, P)
    t = 0
    sign = True    # 是否成功连接
    while sign:
        n = t/(3*P)
        m = t/(3*M*P)
        r = ((r0+n-1) % M)+1
        i = ((i0+m-1) % P)+1
        c = int(JSHopping(M, P, r, i, t))
        t = t+1

        packed = b'\x01\x01' + Ck[c].to_bytes(1, byteorder='big', signed=False)
        # ser.write(packed)
        # 高、低地址、信道
        SendData.SendPacket(b'NEWPOI', deviceID, 0x00, 0x00, channel, packed)
        time.sleep(2)
        buf = SendData.ReceiveData()
        if buf == b'retNEW':
            sign = False
    return packed


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
