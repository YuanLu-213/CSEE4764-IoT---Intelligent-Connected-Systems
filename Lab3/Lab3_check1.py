from machine import Pin, I2C, RTC, Timer
import ssd1306
import utime


mode = 0
x = 0

def change_mode_A(pin):
    global mode
    utime.sleep_ms(100)
    mode += 1
        
        

def increase_B(pin, x):
    print('B')
    utime.sleep_ms(100)
    current = list(rtc.datetime())
    current[x] += 1
    rtc.datetime(current)
    

def decrease_C(pin, x):
    print('C')
    utime.sleep_ms(100)
    current = list(rtc.datetime())
    current[x] -= 1
    rtc.datetime(current)
                

button_A = Pin(0, Pin.IN)
button_B = Pin(16, Pin.IN)
button_C = Pin(2, Pin.IN)


i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

rtc = RTC()
rtc.datetime((2021, 9, 29, 0, 10, 32, 36, 0))

while True:
    display.fill(0)
    mode_display = ""
    time = rtc.datetime()
    date_str = str(time[0]) + '/' + str(time[1])+ '/' + str(time[2])
    time_str = str(time[4]) + ':' + str(time[5])+ ':' + str(time[6])
    
    if not button_A.value():
        change_mode_A(button_A)
    if not button_B.value():
        increase_B(button_B, x)
    if not button_C.value():
        decrease_C(button_C, x)
   
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
 
    display.text(mode_display,0,0,1 )
    display.text(date_str,0,10,1)
    display.text(time_str,0,20,1)
    display.show()


    
    #utime.sleep_ms(1)