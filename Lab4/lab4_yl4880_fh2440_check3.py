import machine, time, ssd1306, network, urequests, ujson
from machine import I2C, Pin

wlan = network.WLAN(network.STA_IF)
API_key = "AIzaSyCu6tINtzHjrCyr_zIeKRcQtN00ys9bM6c"
url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_key

lat = None
lon = None

def do_connect():
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.active(True)
        wlan.connect('Columbia University', '')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
do_connect()
i2c = I2C(scl=Pin(5), sda=Pin(4))
display = ssd1306.SSD1306_I2C(128, 32, i2c)

header = {"Content-Type": "application/json"}
request = {"considerIp": "true"}
res = urequests.post(url, headers = header,  data = ujson.dumps(request))
location_info = ujson.loads(res.content)["location"]

lat = location_info["lat"]
lon = location_info["lng"]
display.fill(0) 

open_weather_key = "07ebcb1e4199c237b78194f1b3ec4d15"
open_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(lon) + "&appid=" + open_weather_key
print(open_weather_url)

open_weather_res = urequests.post(open_weather_url)
weather = ujson.loads(open_weather_res.content)

temp = weather['main']['temp']
humid = weather['main']['humidity']
des = weather['weather'][0]['description']

display_1 = "Tmp: " + str(temp)
display_2 = "Humidity: " + str(humid)
display_3 = des

display.text(display_1,0,0,1)
display.text(display_2,0,10,1)
display.text(display_3,0,20,1)
display.show()
