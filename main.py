# M5stack WiFi setup for InfluxDB data streaming
#
# Guides:
# http://docs.micropython.org/en/v1.8.7/esp8266/esp8266/tutorial/network_basics.html
# https://docs.influxdata.com/influxdb/v1.8/guides/write_data/

# Python libraries
import network
import urequests as requests
import time

# M5stack libraries
from m5stack import *
from m5ui import *
from uiflow import *
import hat

############################# WiFi Setup ######################################
# Connect the IoT device to the WiFi
W_ssid = "Private Network"
W_pwd = ""
FirstLine = M5TextBox(75,10,"",lcd.FONT_Default,0xFFFFFF,rotate=90)

# Retrieve a station and check if already connected
station = network.WLAN(network.STA_IF)
if station.isconnected() == True:
    wifi = "Already connected"
else:
    # Connect to station
    station.active(True)
    station.connect(W_ssid,W_pwd)
    wait_ms(2000)

# Retest connection
if station.isconnected() == True:
    wifi = ''.join(station.ifconfig())
else:
    wifi = "Not connected"

# Display status
FirstLine.setText(wifi)

############################# Server Setup ####################################
# Declare url with protocol and host
InfluxDB_url = "http://3.14.28.95:8086/write?db=m5stack"

############################# Sensors Setup ###################################
# Retrieve hat environment on M5stack
hat_env = hat.get(hat.ENV)

# Initialize sensor variables
temperature=None
humidity=None
pressure=None
sensor_data_template = "environment,sensor=m5stack temperature={},humidity={},pressure={}"
printout_template = "T:{},H:{},P:{}"

############################# Display Setup ###################################
# Text box to display data
SecondLine = M5TextBox(55,10,"",lcd.FONT_Default,0xFFFFFF,rotate=90)

############################# Measure and stream ##############################
# Retrieve sensor data and send to server, display data on device as well
while True:
    # Sensor data
    temperature = hat_env.temperature
    humidity = hat_env.humidity
    pressure = hat_env.pressure

    # Send data to server
    sensor_data = sensor_data_template.format(temperature,humidity,pressure)
    data_post = requests.post(InfluxDB_url,data=sensor_data)

    # Update text on device
    SecondLine.setText(printout_template.format(temperature,humidity,pressure))

    # Wait before repeating cycle
    wait_ms(2000)
