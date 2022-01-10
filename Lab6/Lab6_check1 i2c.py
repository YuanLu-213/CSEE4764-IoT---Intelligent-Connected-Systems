from machine import Pin, I2C
import ssd1306
import network, time, urequests, usocket, utime

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('', '')
        while not wlan.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

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

serversocket = usocket.socket(usocket.AF_INET,usocket.SOCK_STREAM)
serversocket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
serversocket.bind(('',80))
serversocket.listen(5)
serversocket.settimeout(1)
text = 'HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n'


i2c = I2C(sda=Pin(4), scl=Pin(5))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

button_A = machine.Pin(2, machine.Pin.IN)

button_A = False

do_connect()

button_A.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_A_Pressed)

url = "http://3.15.219.49:8080/"

while True:
    if button_A:
        print("recording")
        data = []
        acc = ADXL345_I2C()
        acc_x, acc_y, _ = acc.xyz
        print(acc_x, acc_y)
        utime.sleep_ms(100)
        data = {'x':acc_x, 'y':acc_y}
        send_data = urequests.post(url + "post", json = data)
        status = send_data.text