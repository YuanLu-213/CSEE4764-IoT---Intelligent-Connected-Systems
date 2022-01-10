from machine import RTC, I2C, Pin, ADC, PWM
import machine, utime, ssd1306, network, urequests, ujson, usocket, ntptime, uselect

mode = 0
wlan = network.WLAN(network.STA_IF)
rtc = RTC()
adc = ADC(0)

def do_connect():
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    return wlan.ifconfig()


ip_address = do_connect()
sock_addr = usocket.getaddrinfo(ip_address[0], 80)[0][-1]
ntptime.settime()
print(rtc.datetime())
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
serversocket = usocket.socket(
    usocket.AF_INET, usocket.SOCK_STREAM)
serversocket.bind(sock_addr)
serversocket.listen(5)
serversocket.settimeout(5)
play_oled = 0
res = "Error"
print('Listening on', sock_addr)
while True:
    #print("1")
    try:
        conn, addr = serversocket.accept()
        print("1")
        print('Got a connection from %s' % str(addr))
        request = conn.recv(2048).decode("utf-8")
        print(request)
        message = request
        if ("Display: time" in message):
            print(message)
            current_datetime = rtc.datetime() 
            date = str(current_datetime[0]) + "-" + str(current_datetime[1]) + "-" + str(current_datetime[2])
            time = str(current_datetime[4]) + ":" + str(current_datetime[5]) + ":" + str(current_datetime[6])
            oled.text(date, 0, 10)
            oled.text(time, 0, 20)
            res = "Time displayed"

            if (play_oled == 1):
                oled.show()
        
        elif ("Spoken_message" in message):
            print(message)
            spoken_message_index = message.find("Spoken_message")
            spoken_message = message[spoken_message_index+16:].split('\n')[0][:-1]
            oled.text(spoken_message, 0, 10)
            res = "Spoken language displayed"

            if (play_oled == 1):
                oled.fill(0)
                oled.text(res, 0, 20)
                oled.show()

        elif ("Display: on" in message):
            print(message)
            play_oled = 1
            oled.text("success", 0,10)
            oled.show()
            res = "Display turned on"
        elif ("Display: off" in message):
            print(message)
            res = "Display turned off"
            oled.fill(0)
            oled.show()
            play_oled = 0
        
        print('Responding')
        conn.send('HTTP/1.1 200 OK\r\n'.encode())
        conn.send('Content-Type: text/html\r\n'.encode())
        conn.send(('Content-Length: ' + str(len(res)) + '\r\n').encode())
        conn.send('Connection: close\r\n\r\n'.encode())
        conn.send(res.encode())
        conn.close()
        print('CLOSED')
    except Exception as ex:
        message = ""
        oled.fill(0)
    
