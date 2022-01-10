import machine, utime, ssd1306, network, urequests, ujson
from machine import I2C, Pin

lat = None
lon = None
mode = 0
wlan = network.WLAN(network.STA_IF)
API_key = "AIzaSyCu6tINtzHjrCyr_zIeKRcQtN00ys9bM6c"
url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_key

twitter_key = "556VDJEVX46EN6JT"
twitter_url = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=" + twitter_key

def do_connect():
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

def button_pressed_A(pin):
    global mode
    utime.sleep_ms(100)
    mode = 1

do_connect()
i2c = I2C(scl=Pin(5), sda=Pin(4))
display = ssd1306.SSD1306_I2C(128, 32, i2c)
button_A = Pin(0, Pin.IN)

header = {"Content-Type": "application/json"}
request = {"considerIp": "true"}
res = urequests.post(url, headers = header,  data = ujson.dumps(request))
location_info = ujson.loads(res.content)["location"]

lat = location_info["lat"]
lon = location_info["lng"]

open_weather_key = "07ebcb1e4199c237b78194f1b3ec4d15"
open_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + open_weather_key
print(open_weather_url)

open_weather_res = urequests.post(open_weather_url)
weather = ujson.loads(open_weather_res.content)

temp = weather['main']['temp']
humid = weather['main']['humidity']
des = weather['weather'][0]['description']

status = "You are at " + str(lat) + " , " + str(lon) + " , " + des 
twitter_url += "&status=" + status
twitter_posted = None

while True:
    display.fill(0)
    
    if not button_A.value():
        button_pressed_A(button_A)
    if mode == 1:
        twitter_res = urequests.post(twitter_url)
        twitter_posted = ujson.loads(twitter_res.content)
        print(twitter_posted)
    utime.sleep_ms(100)
    mode = 0
    
    if twitter_posted == 1:
        display.text(status, 0, 10, 1)
        display.show()

