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

print(location_info)

lat = location_info["lat"]
lon = location_info["lng"]

display.fill(0) 

display1 = "Lat:" + str(lat)
display2 = "Lng:" + str(lon)

display.text(display1, 0, 10)
display.text(display2, 0, 20)

display.show()  

