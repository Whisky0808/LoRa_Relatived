from fall import Fall
from types import MethodType

from sense_hat import SenseHat

sense = SenseHat()
sense.clear()
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
#新的跌倒响应函数
def direction_fall(self):
    print('out xiangying')
    sense.set_pixels(question_mark)


# 实例代码修改相应函数
#创建实例
my_fall = Fall()
#替换跌倒响应函数
my_fall.direction_fall = MethodType(direction_fall, my_fall)
#启动
my_fall.start()

#后面的代码不受影响
while True:
    print("xunhuaning")