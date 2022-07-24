from sense_hat import SenseHat

import time
import math
sense = SenseHat()

sense.set_imu_config(False, True, False)

#global 
data_x = [1,2,3,4,5,6,7,8,9,10]
data_y = [1,2,3,4,5,6,7,8,9,10]
data_y = [1,2,3,4,5,6,7,8,9,10]

while True:
    sum_x = 0
    sum_y = 0
    sum_z = 0
    count = 1
    while count < 10:
        raw = sense.get_accelerometer_raw()
        sum_x += raw['x']
        sum_y += raw['y']
        sum_z += raw['z']
        count +=1
    
    smv =  math.sqrt(sum_x*sum_x+sum_y*sum_y+sum_z*sum_z)
    
    
    with open('data_xyz.txt','a') as f:
        try:
            f.write("%.2f %.2f %.2f\n" %(sum_x/10,sum_y/10,sum_z/10))
        except KeyboardInterrupt:
            print('error')
        f.close()
    
    with open('data_fiter.txt','a') as f:
        try:
            f.write("%.2f\n" %smv)
        except KeyboardInterrupt:
            print('write data_fiter')
        f.close()
        
    print("x:%.2f y:%.2f z:%.2f" %(sum_x/10,sum_y/10,sum_z/10))
    print("smv:%.2f" %smv)
    time.sleep(0.1)
