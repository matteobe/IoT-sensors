# M5stack WiFi setup for InfluxDB data streaming
#
# Guides:
# http://docs.micropython.org/en/v1.8.7/esp8266/esp8266/tutorial/network_basics.html
# https://docs.influxdata.com/influxdb/v1.8/guides/write_data/
#
# Python libraries
# https://makeblock-micropython-api.readthedocs.io/en/latest/library/usocket.html
# http://docs.micropython.org/en/v1.8.7/esp8266/esp8266/tutorial/network_tcp.html

# Python libraries
import network
import usocket as socket
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
# Declare the server characteristics
server_protocol = "http"
server_host = "3.14.28.95"
server_port = "8086"
server_query = "write?db=m5stack"

# Create a socket that can be used to connect and send data
sock_ai = socket.getaddrinfo(server_host,server_port,0,socket.SOCK_STREAM)
sock_ai = sock_ai[0]

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
ThirdLine = M5TextBox(35,10,"",lcd.FONT_Default,0xFFFFFF,rotate=90)

############################# Measure and stream ##############################
# Define maximum number of points and counter
points_max = 100
points_current = 0

# Tell the user the sensor will start sending now
FirstLine.setText("Sensor sending...")

# Retrieve sensor data and send to server, display data on device as well
while points_current < points_max:
    # Send new datapoint
    points_current += 1

    # Sensor data
    temperature = hat_env.temperature
    humidity = hat_env.humidity
    pressure = hat_env.pressure

    # Build data string to be sent to server
    sensor_data = sensor_data_template.format(temperature,humidity,pressure)

    # Connect to server, send data and close socket
    try:
        sock = socket.socket(sock_ai[0],sock_ai[1],sock_ai[2])
        sock.connect(sock_ai[-1])
        sock.write(b"%s /%s HTTP/1.0\r\n" % ("POST",server_query))
        sock.write(b"Content-Length: %d" % len(sensor_data))
        sock.write(sensor_data)
        sock.close()
    except:
        sock.close()

    # Update texts on device
    SecondLine.setText("Current point: {}".format(points_current))
    ThirdLine.setText(printout_template.format(temperature,humidity,pressure))

    # Wait before repeating cycle
    wait_ms(2000)

# Tell user the sensor has stopped sending after the agreed number of points
FirstLine.setText("Sensor sent {} points".format(points_max))
SecondLine.setText("Program finished")
ThirdLine.setText("")
