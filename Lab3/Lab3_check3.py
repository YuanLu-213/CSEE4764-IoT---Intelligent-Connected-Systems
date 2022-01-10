from machine import Pin, I2C, RTC, Timer, PWM, ADC
import ssd1306
import utime
import time


mode = 0
x = 0
adc = ADC(0)
start = 0
alarm = [0,0,0,0,0,0,0,0]
alarm_set = False

def change_mode_A(pin):
    global mode, alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    mode += 1
        
        

def increase_B(pin, x):
    print('B')
    global alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    current_time = list(rtc.datetime())
    if mode == 9:
        print(mode)
        alarm[x] += 1
        if alarm[x] > 23:
            alarm[x] = 0
    elif mode == 10:
        alarm[x] += 1
        if alarm[x] > 59:
            alarm[x] = 0
    else:
        current_time[x] += 1
    rtc.datetime(current_time)
    

def decrease_C(pin, x):
    print('C')
    global alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    current_time = list(rtc.datetime())
    
    if mode == 9:
        print(mode)
        alarm[4] -= 1
        if alarm[4] < 0:
            alarm[4] = 23
    elif mode == 10:
        alarm[5] -= 1
        if alarm[5] < 0:
            alarm[5] = 59
    else:
        current_time[x] -= 1
    rtc.datetime(current_time)

def alarm_check():
    global alarm_set, hour_str, min_str, alarm_str
    current = list(rtc.datetime())
    if current[4] == alarm[4] and current[5] == alarm[5]:
        return True
    else: return False

button_A = Pin(0, Pin.IN)
button_B = Pin(16, Pin.IN)
button_C = Pin(2, Pin.IN)
p12 = Pin(13, Pin.OUT, Pin.PULL_UP)
pwm12 = PWM(p12)
pwm12.freq(0)


i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

rtc = RTC()
rtc.datetime((2021, 9, 29, 0, 1, 1, 40, 0))

while True:
    display.fill(0)
    mode_display = ""
    current_time = rtc.datetime()
    date_str = str(current_time[0]) + '/' + str(current_time[1])+ '/' + str(current_time[2])
    time_str = str(current_time[4]) + ':' + str(current_time[5])+ ':' + str(current_time[6])
    brightness = adc.read() / 1024
    display.contrast(int(brightness * 100))
    hour_str = str(alarm[4])
    min_str = str(alarm[5])
    alarm_str = hour_str + ":" + min_str
    
    
    if not button_A.value():
        change_mode_A(button_A)
    if not button_B.value():
        increase_B(button_B, x)
    if not button_C.value():
        decrease_C(button_C, x)
    
    if not alarm_set:
        alarm = [0,0,0,0,0,0,0,0]

    else:
        if alarm_check():
            start = time.ticks_ms()
            pwm12.freq(1023)
            if pwm12.freq() > 0:
                #timer = time.ticks_diff(time.ticks_ms(), start)
                if start > 50000:
            #utime.sleep_ms(5000)
                    alarm = [0,0,0,0,0,0,0,0]
                    pwm12.freq(0)
                    alarm_set = False
                
    if (mode == 1):
        mode_display += "Edit Year"
        x = 0
    if (mode == 2):
        mode_display += "Edit Month"
        x = 1
    if (mode == 3):
        mode_display += "Edit Day"
        x = 2
    if (mode == 4):
        mode_display += "Edit Hour"
        x = 4
    if (mode == 5):
        mode_display += "Edit Minute"
        x = 5
    if (mode == 6):
        mode_display += "Edit Second"
        x = 6
    if (mode == 7):
        mode_display += "Time Confirmed!!"
    if (mode == 8):
        mode_display += "Set Alarm"
        alarm_set = True
    if (mode == 9):
        mode_display += "Set Hour"
        x = 4
        display.text(alarm_str, 70, 20, 1 )
    if (mode == 10):
        mode_display += "Set Minute"
        x = 5
        display.text(alarm_str, 70, 20, 1 )
    if (mode == 11):
        mode_display += "Alarm Set!!"
        alarm_set = False
    if (mode == 12):
        mode_display += "Screen Brightness"
        mode_display = "Light sensor"
        date_str = "Reading:" + str(adc.read())
        time_str = "Brightness:" + str(int(brightness * 100)) + "%"
    if (mode == 13):
        mode = 0
    
    display.text(mode_display,0,0,1 )
    display.text(date_str,0,10,1)
    display.text(time_str,0,20,1)
    display.show()