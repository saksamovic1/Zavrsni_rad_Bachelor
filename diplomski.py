from ST7735 import TFT
from sysfont import sysfont
from terminalfont import terminalfont
from seriffont import seriffont
from machine import SPI, Pin, PWM
import dht
import machine
import time
import ntptime
import math
import network
import urequests
from umqtt.robust import MQTTClient
from machine import WDT  

wdt = WDT(timeout=60000)  #enable it with a timeout of 2s

ntptime.host = "1.europe.pool.ntp.org"

spi = SPI(1, baudrate=20000000, polarity=0, phase=0, sck=Pin(14), mosi=Pin(13))
tft=TFT(spi,16,17,18)
tft.initr()
tft.rgb(True)


mqtt_client_id      = bytes('client_'+'12321', 'utf-8') # Just a random client ID

ADAFRUIT_IO_URL     = 'io.adafruit.com' 
ADAFRUIT_USERNAME   = 'sandinapuff'
ADAFRUIT_IO_KEY     = 'aio_ukMa37ptVoxRjPD93oP6lNLF3i7c' 

TOGGLE_FEED_ID1      = 'increase'
TOGGLE_FEED_ID2      = 'decrease'

led = Pin(22, Pin.OUT)
sensor = dht.DHT11(Pin(23))
timer = machine.Timer(0)

pwm = PWM(led)

measured_temp = 0
set_temp = 0
click = 0
change_theme = 0
options = "display"
counter = 0

sel = Pin(25, Pin.IN)
down = Pin(26, Pin.IN)
up = Pin(27, Pin.IN)

TZ = 2
def measure_data(t): # measuring data function - temperature
    global options
    global measured_temp
    global counter 
    try:
        sensor.measure()
    except:
        print("Problem measuring.") 
        counter += 1 
        if (counter == 5):
            counter = 0 
            machine.reset() 
    measured_temp = sensor.temperature()
    refresh_data(1)
    if (options == "display"):
        return_to_display()
    if (options == "options"):
        print_display_options()
    if (options == "weather"): 
        print_display_weather()

def connect_wifi(): # wireless connecting function
    global wifi
    wifi = network.WLAN(network.STA_IF)  
    wifi.active(True)
    wifi.disconnect()
    wifi.connect("BFAM", "neradinaminternet")
    if not wifi.isconnected():
        print('connecting..')
        tft.text((0,0), "connecting...", TFT.BLUE, terminalfont, 1)
        timeout = 0
        while (not wifi.isconnected() and timeout < 5):
            print(5 - timeout)
            timeout = timeout + 1
            time.sleep(1) 
    if(wifi.isconnected()):
        print('connected')
        tft.text((0,20), "connected", TFT.BLUE, terminalfont, 1)
    else:
        print('not connected')
        tft.text((0,20), "not connected", TFT.BLUE, terminalfont, 1)
       # sys.exit()

def refresh_data(t): # time, date and weather data collecting and refreshing
    global temperatureout
    global desc
    global timestamp
    global datestamp
    hour = 0
    minute = 0
    try:
        timenow = time.localtime()
    except:
        print("Error in getting time")
    if (timenow[3] + TZ < 10):
        hour = '0' + str(timenow[3] + TZ)
    else:
        hour = str(timenow[3] + TZ)
    if (timenow[4] < 10):
        minute = '0' + str(timenow[4])
    else: 
        minute = str(timenow[4])
    mjesec = 0
    dan = 0
    if (timenow[2] < 10):
        dan = '0' + str(timenow[2])
    else:
        dan = str(timenow[2])
    if (timenow[1] < 10):
        mjesec = '0' + str(timenow[1])
    else:
        mjesec = str(timenow[1])
    datestamp = dan + '.' + mjesec + '.' + str(timenow[0])
    timestamp = hour + ':' + minute
    try:
        r = urequests.get("http://api.openweathermap.org/data/2.5/weather?q=Sarajevo&appid=f9e419c8159165c16940b544681bdd30").json()
        desc = r["weather"][0]["description"]
        temperatureout = r["main"]["temp"] - 273.15
    except:
        print("Error in receiving data")

def print_temp_value(temp, y, font_size1, font_size2, color):
    global x, deltax
    if (temp >= 0 and temp < 10):
        if (font_size1 == 4):
            x = 51
            deltax = 32
        else:
            x = 67
            deltax = 18
    elif ((temp < 0 and temp > -10) or temp >= 10):
        if (font_size1 == 4):
            x = 40
            deltax = 54
        else:
            x = 60
            deltax = 29
    tft.text((x, y), str(temp), color, terminalfont, font_size1)
    tft.circle((x + deltax, y), font_size2, color)
    tft.text((x + deltax + 2, y), "C", color, terminalfont, font_size1)

def print_display(color1, color2, color3): # printing first page on display
    tft.fill(TFT.BLACK)
    print_temp_value(measured_temp, 55, 4, 3, color1)
    print_temp_value(set_temp, 30, 2, 1, color2)
    tft.circle((80, 63), 50, color3)

def print_display_options(): # printing options page
    tft.fill(TFT.BLACK)
    if (change_theme == 0):
        color1 = TFT.BLUE
        color2 = color3 = color4 = TFT.GRAY
    elif (change_theme == -1):
        color2 = TFT.BLUE
        color1 = color3 = color4 = TFT.GRAY
    elif (change_theme == -2):
        color3 = TFT.BLUE
        color2 = color1 = color4 = TFT.GRAY
    elif (change_theme == -3):
        color4 = TFT.BLUE
        color2 = color3 = color1 = TFT.GRAY 
    tft.text((17, 25), "Dark_Blue", color1, terminalfont, 2)
    tft.text((17, 45), "Green", color2, terminalfont, 2)
    tft.text((17, 65), "Light_Blue", color3, terminalfont, 2)
    tft.text((17, 85), "Red", color4, terminalfont, 2)

def print_display_weather(): # printing weather page
    tft.fill(TFT.BLACK)
    if (change_theme == 0):
        color1 = TFT.PURPLE
        color2 = TFT.WHITE
        color3 = TFT.BLUE
    elif (change_theme == -1):
        color1 = TFT.YELLOW
        color2 = TFT.WHITE
        color3 = TFT.GREEN
    elif (change_theme == -2):  
        color1 = TFT.YELLOW_PASTEL
        color2 = TFT.WHITE
        color3 = TFT.FOREST 
    elif (change_theme == -3):
        color1 = TFT.WHITE   
        color2 = TFT.GRAY 
        color3 = TFT.MAROON   
    if (len(desc) <= 5):           
        tft.text((66, 15), desc, color1, terminalfont, 1)
    elif (len(desc) > 5 and len(desc) <= 7):       
        tft.text((62, 15), desc, color1, terminalfont, 1)
    elif (len(desc) > 7 and len(desc) <= 10):       
        tft.text((51, 15), desc, color1, terminalfont, 1)    
    elif (len(desc) > 10 and len(desc) <= 13):       
        tft.text((36, 15), desc, color1, terminalfont, 1)
    elif (len(desc) > 13 and len(desc) <= 15): 
        tft.text((30, 15), desc, color1, terminalfont, 1)
    elif (len(desc) > 15): 
        tft.text((26, 15), desc, color1, terminalfont, 1)
    print_temp_value(round(temperatureout), 30, 2, 1, color2)
    tft.text((18, 53), timestamp, color3, terminalfont, 4) 
    tft.text((18, 90), datestamp, color2, terminalfont, 2) 
     
def testroundrects(): # rectangles animation at start
    tft.fill(TFT.BLACK);
    color = 100 
    for t in range(5):
        x = 0
        y = 0
        w = tft.size()[0] - 2
        h = tft.size()[1] - 2
        for i in range(17):
            tft.rect((x, y), (w, h), color)
            x += 2
            y += 3
            w -= 4
            h -= 6
            color += 1100
        color += 100
    tft.text((32,55), "sandina", TFT.BLUE, terminalfont, 2)

def change_temp(value): # increase or decrease set temperature
    global click 
    global set_temp
    click += 1
    set_temp += value
    time.sleep_ms(20)
    click = 0

def selection(arrow): # changing themes
    global click
    global change_theme
    click += 1
    change_theme += arrow
    if (change_theme == 1):
        change_theme = -3
    if (change_theme == -4):
        change_theme = 0
    time.sleep_ms(20)
    click = 0

def initialize_app():
    global set_temp
    global measured_temp
    tft.fill(TFT.BLACK)
    tft.rotation(1) # set display rotation
    pwm.init()
    pwm.freq(30000)
    pwm.duty(1023)
    connect_wifi() # connect to wifi
    time.sleep_ms(1500)
    tft.fill(TFT.BLACK)
    testroundrects() 
    time.sleep_ms(1000)
    tft.fill(TFT.BLACK)
    try:
        sensor.measure()
    except:
        print("Problem measuring.")
    set_temp = measured_temp = sensor.temperature()
    ntptime.settime() 
    refresh_data(0)
    return_to_display()
    
    timer.init(period=30000, mode=machine.Timer.PERIODIC, callback=measure_data) # measure data every 30 seconds

def return_to_display():
    if (change_theme == 0):
        print_display(TFT.BLUE, TFT.WHITE, TFT.PURPLE)
    elif (change_theme == -1):
        print_display(TFT.GREEN, TFT.WHITE, TFT.YELLOW)
    elif (change_theme == -2):
        print_display(TFT.FOREST, TFT.WHITE, TFT.YELLOW_PASTEL)
    elif (change_theme == -3):
        print_display(TFT.MAROON, TFT.WHITE, TFT.GRAY)

initialize_app()

client = MQTTClient(client_id=mqtt_client_id, 
                    server=ADAFRUIT_IO_URL, 
                    user=ADAFRUIT_USERNAME, 
                    password=ADAFRUIT_IO_KEY,
                    ssl=False) 
try:            
    client.connect()  
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))

def cb(topic, msg):                             # Callback function
    global set_temp
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    recieved_data = str(msg,'utf-8')            #   Recieving Data
    if (recieved_data=="1"):
       if (topic == b'sandinapuff/feeds/increase'):
           set_temp += 1
       else:
           set_temp -= 1
       return_to_display()
         
        
toggle_feed_up = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TOGGLE_FEED_ID1), 'utf-8') # format - sandinapuff/feeds/increase
toggle_feed_down = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_USERNAME, TOGGLE_FEED_ID2), 'utf-8') # format - sandinapuff/feeds/decrease 
client.set_callback(cb)      # Callback function               
client.subscribe(toggle_feed_up) # Subscribing to particular topic
client.subscribe(toggle_feed_down) # Subscribing to particular topic
 

while True:
    if (up.value() and not click and options != "options" and options != "weather"): # increase value while in display mode
        change_temp(1)
        options = "display"
        return_to_display()
    elif (down.value() and not click and options != "options" and options != "weather"): # decrease value while in options mode
        change_temp(-1)
        options = "display"
        return_to_display()
    elif (up.value() and not click and options == "options"): # up button in options mode
        selection(1)
        print_display_options()
    elif (down.value() and not click and options == "options"): # down button in options mode
        selection(-1)
        print_display_options()
    elif (sel.value() and not click and options != "options" and options != "weather"): # sel button when not in options or in wheather
        options_timer = 0 # timer to check if sel button is held
        while (sel.value()):
            options_timer += 1
            time.sleep(1)
        if (options_timer >= 2): # sel button held more than 2 seconds - options mode
            options = "options"
            tft.fill(TFT.BLACK)
            tft.text((39, 52), "THEMES", TFT.GRAY, terminalfont, 2)
            time.sleep(1.5)
            print_display_options()
        else: # sel button clicked once - weather mode
            options = "weather" 
            print_display_weather() 
        change_temp(0)
    elif (sel.value() and not click and options != "display"): # sel button when not in options or in wheather
        click += 1
        options = "display"
        return_to_display()
        time.sleep_ms(20)
        click = 0
    if (not wifi.isconnected()): 
        connect_wifi() 
    try:
        client.check_msg()
    except:
        client.disconnect()
        try:            
            client.connect()  
        except Exception as e:
            print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    wdt.feed()
    time.sleep_ms(100)
