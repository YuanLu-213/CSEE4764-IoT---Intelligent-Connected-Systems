from machine import Pin, I2C, RTC, Timer, PWM, ADC
import ssd1306
import utime
import time



x_axis = 0
y_axis = 10
max_value = 32767
x_min = 0
x_max = 128
y_min = -10
y_max = 32
    
def write(hexx, value):
    global cs, hspi
    utime.sleep_ms(100)
    cs.value(0)
    hspi.write(hexx)
    hspi.write(value)
    cs.value(1)

def read(hexx):
    global cs, hspi
    buffer = bytearray(2)
    cs.value(0)
    read_mode = 1 << 7
    addr = read_mode | hexx
    #print('addr ', addr)
    hspi.readinto(buffer, addr)
    cs.value(1)
    #print(buffer)
    return buffer

def moves(value, speed):
    global max_value
    axis_moves = int(value / 255) * speed
    return axis_moves
'''    
def x_range(x):
    global x_min, x_max
    if x > x_max:
        x_axis =  x_min
    elif x < x_min:
        x_axis = x_max
    return x_axis
    
def y_range(y):
    global y_min, y_max
    if y > y_max:
        y_aixs = y_min
    elif y < y_min:
        y_aixs = y_max
    return y_aixs
'''
i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

hspi = machine.SPI(1, baudrate=1500000, polarity=1, phase=1)
cs = Pin(15, Pin.OUT)
cs.value(1)

rtc = RTC()
rtc.datetime((2021, 9, 29, 0, 1, 58, 45, 0))

#write(b'\x2C', b'\x0A')
#write(b'\x2D', b'\x28')
#write(b'\x31', b'\x0C')
write(b'\x31', b'\x0C')
write(b'\x2c', b'\x0a')
write(b'\x2e', b'\x00')
write(b'\x38', b'\x00')
write(b'\x2d', b'\x08')

while True:
    x0 = read(0xb2) 
    x1 = read(0xb3)   
    y0 = read(0xb4)     
    y1 = read(0xb5)
    #utime.sleep_ms(100)
    #continue

    display.fill(0)
    current_time = rtc.datetime()
    date_str = str(current_time[0]) + '/' + str(current_time[1])+ '/' + str(current_time[2])
    time_str = str(current_time[4]) + ':' + str(current_time[5])+ ':' + str(current_time[6])

    
    x_value = x1[1] << 8 | x0[1]
    y_value = y1[1] << 8 | y0[1]
    
    #print(x_value,y_value)

    
    if x_value > max_value:
        x_value -= 65536
    if y_value > max_value:
        y_value -= 65536
    
    #print(x_value)
    x_moves = moves(x_value, 3)
    y_moves = moves(y_value, 3)
    #print(x_moves)
    #print(x_moves, y_moves)
    x_axis += x_moves
    y_axis += y_moves
    #print(x_axis)
    #x_axis = x_range(x_axis)
    #print(y_axis)
    if x_axis > x_max:
        x_axis =  x_min
    elif x_axis < x_min:
        x_axis = x_max
    #y_axis = y_range(y_axis)
    if y_axis > y_max:
        y_axis = y_min
    elif y_axis < y_min:
        y_axis = y_max
    
    #print(y_axis)

    display.text(time_str,x_axis,y_axis,1)
    display.show()
    utime.sleep_ms(50)