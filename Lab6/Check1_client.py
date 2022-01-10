from machine import Pin, I2C, RTC, Timer, PWM, ADC
import ssd1306
import utime
import time
import urequests
import ujson
import network



def do_connect():#the function for connecting to network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('STAYSAFE', '20210901ph4')#using the local WIFI name and password
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def button_A_Pressed(pin):
    global button_A
    value = pin.value()
    time.sleep_ms(20)
    if pin.value() != value:
        return
    button_A = True
    
class ADXL345_I2C:
    def __init__(self, addr=0x53):
        self.addr = addr
        self.i2c = I2C(Pin(5), Pin(4))
        self.i2c.writeto_mem(self.addr, 0x2c, b'\x0a')  # 100Hz, disable low power
        self.i2c.writeto_mem(self.addr, 0x2e, b'\x00')  # Disable all interrupts
        self.i2c.writeto_mem(self.addr, 0x38, b'\x00')  # Disable FIFO
        self.i2c.writeto_mem(self.addr, 0x2d, b'\x08')  # Start measuring
        self.buff = bytearray(6)

    def discard_initial(self, n_samples, wait_ms):
        for i in range(n_samples):
            self.buff = self.i2c.readfrom_mem(self.addr, 0x32, 6)
            utime.sleep_ms(wait_ms)

    @property
    def xyz(self):
        self.buff = self.i2c.readfrom_mem(self.addr, 0x32, 6)
        x = (int(self.buff[1]) << 8) | self.buff[0]
        y = (int(self.buff[3]) << 8) | self.buff[2]
        z = (int(self.buff[5]) << 8) | self.buff[4]
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        return x, y, z
    
    
i2c = I2C(sda=Pin(4), scl=Pin(5))    

do_connect()#run the function to connect the network

#button_A = machine.Pin(2, machine.Pin.IN)
#b_A_value = False
#button_A.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_A_Pressed)
acc = ADXL345_I2C()
round_num = 0
label = "C"
sample = []
while True:
    #if b_A_value:False
    for i in range(20):
        for j in range(20):
            utime.sleep_ms(100)
            acc_x, acc_y, _ = acc.xyz
            #print(acc_x, acc_y)
            sample.append(acc_x)
            sample.append(acc_y)
        round_num += 1
        data = {"round": round_num, "label": label, "sample":sample}
        sample = []
        print(data)
    response = urequests.post(
        'http://18.117.11.129:5000',
        data = ujson.dumps(
            data
        ))
    response.close()