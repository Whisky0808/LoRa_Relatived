# 必须的一些头文件
import time
import math
import threading

from sense_hat import SenseHat

DIRECTION_FALL = 'fall'
DIRECTION_SOS = 'sos'

sense = SenseHat()



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


def fall_forward_or_backward():
    orientation = sense.get_orientation_degrees()
    if 60 < orientation['roll'] < 120:
        return False
    else:
        return True


def fall_left_or_right():
    orientation = sense.get_orientation_degrees()
    if 60 > orientation['pitch'] > 0:

        return False
    elif 330 < orientation['pitch'] < 360:

        return False
    else:
        print("P:{pitch}, R:{roll}, Y:{yaw}".format(**orientation))
        return True

# 继承线程类
class Fall(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = "SenseHat_Fall"
        self.__a = None
        # 按钮事件处理函数赋值。
        #sense.stick.direction_any = self.press_button

    # 跌倒的相应函数，现在是把LED设为全红，可以通过MethodType动态修改相应函数
    def direction_fall(self):
        sense.set_pixels(question_mark)
        print('backward over')

    # 按钮求救相应函数，这里是重新封装了。
    def press_button(self):
        sense.show_message('press')

    def run(self):
        while True:
            sum_x = 0
            sum_y = 0
            sum_z = 0
            count = 1
            # 窗口为十的中值滤波
            while count < 10:
                raw = sense.get_accelerometer_raw()
                sum_x += raw['x']
                sum_y += raw['y']
                sum_z += raw['z']
                count += 1

            smv = math.sqrt(sum_x * sum_x + sum_y * sum_y + sum_z * sum_z)
            # smv的阈值设置为5~13
            if smv > 13 or smv < 5:
                time.sleep(1)
                # 调用相应的相应函数
                if fall_forward_or_backward():
                    self.direction_fall()

                elif fall_left_or_right():
                    self.direction_fall()

            # print("smv:%.2f" %smv)
            orientation = sense.get_orientation_degrees()
            # angle = abs(360-orientation['pitch'])+abs(270-orientation['roll'])+abs(0-orientation['yaw'])
            # print("angle %f" %angle)
            # print("P:{pitch}, R:{roll}, Y:{yaw}".format(**orientation))
            time.sleep(0.1)
