from machine import Pin, I2C, RTC, Timer, PWM, ADC
import ssd1306, time, utime, network, urequests, ujson, ntptime
import Weather, Twitter

API_key = "AIzaSyCu6tINtzHjrCyr_zIeKRcQtN00ys9bM6c"
url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_key

wlan = network.WLAN(network.STA_IF)
mode = 0
x = 0
rtc = RTC()
adc = ADC(0)
start = 0
alarm = [0,0,0,0,0,0,0,0]
alarm_set = False
lat = None
lon = None
temp = None
des = None
last_tweet = ""

button_A = Pin(2, Pin.IN)
button_B = Pin(16, Pin.IN)
button_C = Pin(0, Pin.IN)
p12 = Pin(12, Pin.OUT)
p12_LED = Pin(12, Pin.OUT)
pwm12 = PWM(p12, freq = 500, duty = 0)
pwm12_LED = PWM(Pin(12), freq = 500, duty = 0)
i2c = I2C(scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

def do_connect():
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    return wlan.ifconfig()

def change_mode_A(pin):
    global mode, alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    mode += 1

def increase_B(pin, x):
    global alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    current_time = list(rtc.datetime())
    if mode == 2:
        alarm[x] += 1
        if alarm[x] > 23:
            alarm[x] = 0
    elif mode == 3:
        print("hello")
        alarm[x] += 1
        if alarm[x] > 59:
            alarm[x] = 0
    

def decrease_C(pin, x):
    global alarm_set, alarm, hour_str, min_str, alarm_str
    utime.sleep_ms(100)
    current_time = list(rtc.datetime())
    
    if mode == 2:
        print(mode)
        alarm[4] -= 1
        if alarm[4] < 0:
            alarm[4] = 23
    elif mode == 3:
        alarm[5] -= 1
        if alarm[5] < 0:
            alarm[5] = 59

def alarm_check():
    global alarm_set, hour_str, min_str, alarm_str
    current = list(rtc.datetime())
    if current[4] == alarm[4] and current[5] == alarm[5]:
        return True
    else: return False
    
def get_geoLocation_and_weather():
    global lat, lon, des, temp  # variable for weather and location
    geoLocation_API_key = "AIzaSyCu6tINtzHjrCyr_zIeKRcQtN00ys9bM6c"
    geoLocation_url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + geoLocation_API_key
    
    openWeather_API_key = "07ebcb1e4199c237b78194f1b3ec4d15"
    openWeather_url = "https://api.openweathermap.org/data/2.5/weather?lat="
    print(open_weather_url)
    header = {"Content-Type": "application/json"}
    request = {"considerIp": "true"}
    res = urequests.post(url, headers = header,  data = ujson.dumps(request))
    location_info = ujson.loads(res.content)["location"]
    lat = location_info["lat"]
    lon = location_info["lng"]
    
    if (lat != None and lon != None):
        open_weather_url = openWeather_url + str(lat) + "&lon=" + str(lon) + "&appid=" + open_weather_key
        open_weather_res = urequests.post(open_weather_url)
        weather = ujson.loads(open_weather_res.content)

        temp = weather['main']['temp']
        des = weather['weather'][0]['description']
    return [lat, lon, temp, des]

def send_twitter(tweet):
    twitter_key = "556VDJEVX46EN6JT"
    twitter_url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=" + twitter_key
    status = tweet
    twitter_url += "&status=" + status
    twitter_res = urequests.post(twitter_url)
    twitter_posted = ujson.loads(twitter_res.content)
    return twitter_posted

do_connect()
ip_address = do_connect()
sock_addr = usocket.getaddrinfo(ip_address[0], 80)[0][-1]
serversocket = usocket.socket(
    usocket.AF_INET, usocket.SOCK_STREAM)
serversocket.bind(sock_addr)
serversocket.listen(5)
serversocket.settimeout(5)
play_oled = 0
res = "Error"
print('Listening on', sock_addr)
ntptime.settime()

while True:
    display.fill(0)
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

    try:
        conn, addr = serversocket.accept()
        print("1")
        print('Got a connection from %s' % str(addr))
        request = conn.recv(2048).decode("utf-8")
        print(request)
        message = request
        if ("Display: time" in message):
            #print(message)
            current_datetime = rtc.datetime() 
            date = str(current_datetime[0]) + "-" + str(current_datetime[1]) + "-" + str(current_datetime[2])
            time = str(current_datetime[4]) + ":" + str(current_datetime[5]) + ":" + str(current_datetime[6])
            oled.text(date, 0, 10)
            oled.text(time, 0, 20)
            res = "Time displayed"
            
            if not alarm_set:
                alarm = [0,0,0,0,0,0,0,0]
            else:
                if alarm_check():
                    #print(pwm12.freq())
                    pwm12.duty(500)
                    pwm12_LED.duty(500)
            # Wait for button press to cancel alarm
                    display.text("alarm!",0,0,1 )
                    display.show()
                while button_A.value():
                    utime.sleep_ms(10)
                
            # Button pressed, alarm cancelled
                    alarm = [0,0,0,0,0,0,0,0]
                    pwm12.duty(0)
                    pwm12_LED.duty(0)
                    alarm_set = False

            if (mode == 1):
                alarm_set = True
            if (mode == 2):
                x = 4
                display.text(alarm_str, 70, 20, 1 )
            if (mode == 3):
                x = 5
                display.text(alarm_str, 70, 20, 1 )
            if (mode == 4):
                alarm_set = False
            if (mode == 5):
                mode = 0
                
            if (play_oled == 1):
                oled.show()
            
        elif ("Display: location" in message):
            res = "Location displayed"
            location = get_geoLocation_and_weather()
            lat = location[0]
            lon = location[1]
            date_str = "Lat:" + str(lat)
            time_str = "Lng:" + str(lon)
            if (play_pled == 1):
                oled.fill(0)
                oled.text(date_str, 0, 10)
                oled.text(time_str, 0, 20)
                oled.show()
            
        elif ("Display: weather" in message):
            res = "Weather displayed"
            weather = get_geoLocation_and_weather()
            temp = weather[2]
            des = weather[3]
            date_str = "Tmp: " + str(temp)
            time_str = des
            if (play_oled == 1):
                oled.fill(0)
                oled.text(date_str, 0, 10)
                oled.text(time_str, 0, 20)
                oled.show()
        
        elif ("Send: tweets" in message):
            res = "Twitter sent"
            print(message)
            tweet_to_send = message.split(" ")[2:]
            date_str = tweet_to_send
            twitter_status = send_twitter(tweet_to_send)
            if (twitter_status == 1):
                last_tweet = tweet_to_send
                if (play_oled == 1):
                    oled.fill(0)
                    oled.text(date_str, 0, 10)
                    oled.show()
                    
        elif ("Last: tweets" in message):
            res = "Last tweet displayed"
            date_str = last_tweet
            if (play_oled == 1):
                oled.fill(0)
                oled.text(date_str, 0, 10)
                oled.show()
            
        elif ("Display: on" in message):
            #print(message)
            play_oled = 1
            oled.text("success", 0,10)
            oled.show()
            res = "Display turned on"
            
        elif ("Display: off" in message):
            #print(message)
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
        oled.text(current_mode, 0, 0)
        oled.text(date_str, 0, 10)
        oled.text(time_str, 0, 20)
#        if play_oled == 1:
#            oled.show()
    except Exception as ex:
        message = ""
        oled.fill(0)