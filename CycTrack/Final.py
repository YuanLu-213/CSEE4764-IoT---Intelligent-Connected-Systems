# import utime
import digitalio
import board
import time
import RPi.GPIO as GPIO
import adafruit_gps
import serial
import requests
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import hx8357  # pylint: disable=unused-import
from datetime import datetime

mode = 0 
emergency = False
state = 0
alt = 0
lat = 40.8191769
log  = 0
speed = 0
temp = None
des = None
clock = ""
BORDER = 20
FONTSIZE = 30
fromaddr = "lixunqi512@gmail.com"
toaddr = "luyuan1998213@gmail.com"
# API_key = "AIzaSyCu6tINtzHjrCyr_zIeKRcQtN00ys9bM6c"
# url = "https://www.googleapis.com/geolocation/v1/geolocate?key=" + API_key
open_weather_key = "07ebcb1e4199c237b78194f1b3ec4d15"

uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# pylint: disable=line-too-long
# Create the display:
disp = hx8357.HX8357(spi, rotation=180,                           # 3.5" HX8357

    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

#define buttons
GPIO.setmode(GPIO.BCM)                             
button_A = 17
button_B = 6
# button_C = 12
GPIO.setup(button_A, GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_B, GPIO.IN,pull_up_down=GPIO.PUD_UP)
# GPIO.setup(button_C, GPIO.IN)

def switch_page(pin):
    global mode
    time.sleep(0.2)
    mode += 1
    if mode == 2:
        mode = 0

def emergency_button(x):
    global emergency
    time.sleep(0.2)
    emergency = not emergency

def GPS():
    global alt, lat, log, speed, clock
    # uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=10)
    # gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
    # gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    # gps.send_command(b"PMTK220,1000")
    last_print = time.monotonic()
    # while True:
    gps.update()
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
    
    if gps.has_fix:    
        print("=" * 40)  # Print a separator line.
        print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,  # month!
                gps.timestamp_utc.tm_sec,
            )
        )
        print("Latitude: {0:.6f} degrees".format(gps.latitude))
        print("Longitude: {0:.6f} degrees".format(gps.longitude))
        print("Fix quality: {}".format(gps.fix_quality))
        # Some attributes beyond latitude, longitude and timestamp are optional
        # and might not be present.  Check if they're None before trying to use!
        if gps.satellites is not None:
            print("# satellites: {}".format(gps.satellites))
        if gps.altitude_m is not None:
            print("Altitude: {} meters".format(gps.altitude_m))
        if gps.speed_knots is not None:
            print("Speed: {} knots".format(gps.speed_knots))
        if gps.track_angle_deg is not None:
            print("Track angle: {} degrees".format(gps.track_angle_deg))
        if gps.horizontal_dilution is not None:
            print("Horizontal dilution: {}".format(gps.horizontal_dilution))
        if gps.height_geoid is not None:
            print("Height geoid: {} meters".format(gps.height_geoid))

        alt = gps.altitude_m
        lat = gps.latitude
        log = gps.longitude
        speed = gps.speed_knots
        # clock = str(gps.timestamp_utc.tm_mon) +"/" + str(gps.timestamp_utc.tm_mday) + "/" + str(gps.timestamp_utc.tm_year) + " " + str(gps.timestamp_utc.tm_hour) + ":" + str(gps.timestamp_utc.tm_min) + ":" + str(gps.timestamp_utc.tm_sec)
        clock = "{}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,  # month!
                gps.timestamp_utc.tm_sec,
            )
        response = requests.get('http://127.0.0.1:3000/' + "add_data/" + str(lat) + "," + str(log))
        time.sleep(1)
    elif not gps.has_fix:
        print("Waiting for fix...")
        alt = 23
        log = -73.9485765
        speed = 20
        clock = datetime.now().strftime('%m/%d/%Y %H:%M:%S')    
        response = requests.get('http://127.0.0.1:3000/' + "add_data/" + str(lat) + "," + str(log))
        time.sleep(1) 
        lat += 0.0001
        # continue

def Speed_page():
    global state
    # pylint: enable=line-too-long
    # -------------------------------------------------------------------
    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    if disp.rotation % 180 == 90:
        height = disp.width  # we swap height/width to rotate it to landscape!
        width = disp.height
    else:
        width = disp.width  # we swap height/width to rotate it to landscape!
        height = disp.height

    image = Image.new("RGB", (width, height))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a green filled box as the background
    draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
    disp.image(image)

    # Draw a smaller inner purple rectangle
    draw.rectangle(
        (10, 10, width - 10, height-260), fill=(120, 200, 150)
    )

    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

    # Draw Some Text
    tim = clock
    (font_width, font_height) = font.getsize(tim)
    draw.text(
        (90, 20, width - 20, height-250),
        tim,
        font=font,
        fill=(0, 0, 0),
    )

    draw.rectangle(
        (10, 70, width - 240, height-200), fill=(120, 200, 150)
    )

    altitude = "Alt: " + str(alt) + "m"
    (font_width, font_height) = font.getsize(altitude)
    draw.text(
        (20, 80, width - 20, height-250),
        altitude,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    draw.rectangle(
        (10, 130, width - 240, height-100), fill=(120, 200, 150)
    )

    weather = "Weather:"
    (font_width, font_height) = font.getsize(weather)
    draw.text(
        (20, 130, width - 20, height-250),
        weather,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    temperature = str(temp) + " Celsius"
    (font_width, font_height) = font.getsize(weather)
    draw.text(
        (20, 160, width - 20, height- 20),
        temperature,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    descri = des
    (font_width, font_height) = font.getsize(weather)
    draw.text(
        (20, 190, width - 20, height- 20),
        descri,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    draw.rectangle(
        (10, 230, width - 240, height-10), fill=(120, 200, 150)
    )

    Latitude = "Lat: " + str(lat) 
    (font_width, font_height) = font.getsize(weather)
    draw.text(
        (20, 230, width - 20, height-20),
        Latitude,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    Longitude = "Log: "  + str(log)
    (font_width, font_height) = font.getsize(weather)
    draw.text(
        (20, 270, width - 20, height-20),
        Longitude,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25),
        fill=(0, 0, 0),
    )

    draw.rectangle(
        (250, 160, width - 10, height-10), fill=(120, 200, 150)
    )

    Speed_1 = "Speed: "
    Speed_2 =  str(speed) + "knots"
    (font_width, font_height) = font.getsize(Speed_1)
    (font_width, font_height) = font.getsize(Speed_2)
    draw.text(
        (275, 180, width - 20, height-100),
        Speed_1,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40),
        fill=(0, 0, 0),
    )
    draw.text(
        (275, 235, width - 20, height-100),
        Speed_2,
        font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40),
        fill=(0, 0, 0),
    )

    if state == 1:
        draw.rectangle(
            (250, 70, width - 10, height-170), fill=(255, 0, 0)
        )
        em =  "Emrgency Reported"
        (font_width, font_height) = font.getsize(em)
        draw.text(
            (260, 95, width - 10, height-100),
            em,
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20),
            fill=(255, 255, 255),
        )
    else:
        draw.rectangle(
            (250, 70, width - 10, height-170), fill=(120, 200, 150)
        )
        em = "Stay Safe"
        (font_width, font_height) = font.getsize(em)
        draw.text(
            (290, 95, width - 10, height-100),
            em,
            font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30),
            fill=(0, 0, 0),
        )
    # Display image.
    disp.image(image)

def Welcom_page():
    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    if disp.rotation % 180 == 90:
        height = disp.width  # we swap height/width to rotate it to landscape!
        width = disp.height
    else:
        width = disp.width  # we swap height/width to rotate it to landscape!
        height = disp.height

    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a green filled box as the background
    draw.rectangle((0, 0, width, height), fill=(255, 255, 255))
    disp.image(image)

    # Draw a smaller inner purple rectangle
    draw.rectangle(
        (BORDER, BORDER, width - BORDER - 1, height - BORDER - 1), fill=(120, 200, 150)
    )

    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

    # Draw Some Text
    text = "WELCOME"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (width // 2 - font_width // 2, height // 2 - font_height // 2),
        text,
        font=font,
        fill=(0, 0, 0),
    )

    # Display image.
    disp.image(image)

def Map_page():
    global emergency, state,mode
    # Create blank image for drawing.
    # Make sure to create image with mode 'RGB' for full color.
    if disp.rotation % 180 == 90:
        height = disp.width  # we swap height/width to rotate it to landscape!
        width = disp.height
    else:
        width = disp.width  # we swap height/width to rotate it to landscape!
        height = disp.height
    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    disp.image(image)

    chromeOptions = Options()
    chromeOptions.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chromeOptions)

    
    # driver = webdriver.Chrome(options=chromeOptions)

    #url = "file:///home/pi/Desktop/gps.html"
    url = f"http://127.0.0.1:3000/" 
    driver.get(url)
    # --------------------------------------------------------
    while True:
        button_A_val = GPIO.input(button_A)
        button_B_val = GPIO.input(button_B)
        if(button_A_val == 0):
            mode = 0
            driver.quit()
            break   

        if (button_B_val == 0):
            emergency_button(button_B)
            if emergency == True:
                send_em()
                state = 1
                emergency = False

            em_image = Image.new("RGB", (width, height))
            draw_em = ImageDraw.Draw(em_image)
            draw_em.rectangle((0, 0, width, height), outline=0, fill=(255, 0, 0))
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
            em1 = "Emergency Sent!"
            (font_width, font_height) = font.getsize(em1)
            draw_em.text(
                (100, 50, width - 20, height-250),
                em1,
                font=font,
                fill=(255, 255, 255),
            )
            em2 = "Help is on the way"
            (font_width, font_height) = font.getsize(em2)
            draw_em.text(
                (100, 160, width - 50, height-350),
                em2,
                font=font,
                fill=(255, 255, 255),
            )
            driver.quit()
            disp.image(em_image)
            break

        GPS()   
        driver.save_screenshot("googletest.png")
        #image = Image.open("tennis.jpg")
        image = Image.open("googletest.png")
        # --------------------------------------------------------

        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))

        # Display image.
        disp.image(image)

def send_em():
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Emergency!"
    body = "My name is Issac Washingtpn. I'm in a bicycle accident. Immediate medical help needed! My location is (lat: " +  str(lat) + " degree, lon: " + str(log) + " degree)."
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "Lixunqi1997")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def weather(key):
    global temp, des
    open_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat=" + str(lat) + "&lon=" + str(log) + "&appid=" + open_weather_key + "&units=metric"
    open_weather_res = requests.post(open_weather_url)
    weather = json.loads(open_weather_res.content)

    temp = weather['main']['temp']
    des = weather['weather'][0]['description']


def main():
    global state, emergency
    Welcom_page()
    time.sleep(2)
    while True:
        GPS()
        weather(open_weather_key)
        button_A_val = GPIO.input(button_A)
        button_B_val = GPIO.input(button_B)
        if button_A_val == 0:
            print("button_A_val")
            switch_page(button_A)
        if button_B_val == 0:
            emergency_button(button_B)
        if(mode == 0):
            Speed_page()
        elif(mode == 1):
            Map_page()
        if emergency == True:
            send_em()
            state = 1
            emergency = False
        print(mode)



    
    

if __name__ == '__main__':
    main()
