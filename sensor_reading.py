#!/usr/bin/env python3

import time
import colorsys
import sys
import ST7735
import decimal
import os
import boto3

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from subprocess import PIPE, Popen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging
from scp import SCPClient
from paramiko import SSHClient

logging.basicConfig(
    filename="/home/pi/custom_script/sensor.log",
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""all-in-one.py - Displays readings from all of Enviro plus' sensors

Press Ctrl+C to exit!

""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)



# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 20
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25

# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    # Scale the values for the variable between 0 and 1
    vmin = min(values[variable])
    vmax = max(values[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
   # logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i in range(len(colours)):
        # Convert the values to colours from red to blue
        colour = (1.0 - colours[i]) * 0.6
        r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        # Draw a 1-pixel wide rectangle of colour
        draw.rectangle((i, top_pos, i + 1, HEIGHT), (r, g, b))
        # Draw a line graph in black
        line_y = HEIGHT - (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    # Write the text at the top in black
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735.display(img)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

def write_to_file(val):
    filename = str(int(time.time()))
    filename = "/home/pi/data/"+filename
    with open(filename, 'w') as writer:
        writer.write(time.strftime(" %Y/%m/%d-%H:%M:%S\n\n"))
        for el in val:
            writer.write("{:>12}: {}\n".format(el[0], el[1]))
    logging.info("Written to %s", filename)
    return filename

def copy_file(filename):
    host = "10.0.0.19"
    port = 22
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(host,port,"pi")
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(filename, '/home/pi/sensor_data/data.txt') # keep history local
        scp.close()

def write_to_s3(filename):
    s3 = boto3.resource('s3')
    s3.Bucket('bucket').upload_file(filename, os.path.basename(filename))
    
# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.55
cpu_temps = [get_cpu_temperature()] * 5
delay = 0.3  

# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]


values = {}

for v in variables:
    values[v] = [1] * WIDTH

output = []
readings = 5
readings_air = 10
# The main loop
try:
    # variable = "temperature"
    avg_data = 0
    bme280.get_temperature()
    time.sleep(delay)
    for i in range(readings):
        unit = "C"
        cpu_temp = get_cpu_temperature()
        # Smooth out with some averaging to decrease jitter
        cpu_temps = cpu_temps[1:] + [cpu_temp]
        avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
        raw_temp = bme280.get_temperature()
        data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
        display_text(variables[0], data, unit)
       
        avg_data += data
        time.sleep(delay)

    output += [str(round((avg_data / readings),2)) + unit] 

    # variable = "pressure"
    avg_data = 0
    for i in range(readings):
        unit = "hPa"
        data = bme280.get_pressure()
        display_text(variables[1], data, unit)

        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit]   

    # variable = "humidity"
    avg_data = 0
    for i in range(readings):
        unit = "%"
        data = bme280.get_humidity()
        display_text(variables[2], data, unit)
        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit]   

    # variable = "light"
    avg_data = 0
    for i in range(readings):
        unit = "Lux"
        data = ltr559.get_lux()
        display_text(variables[3], data, unit)
        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit]   

    # variable = "oxidised"
    avg_data = 0
    data = gas.read_all() # read once as the first reading is bad
    for i in range(readings):
        unit = "kO"
        data = gas.read_all()
        data = data.oxidising / 1000
        display_text(variables[4], data, unit)
        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit]   

    # variable = "reduced"
    avg_data = 0
    for i in range(readings):
        unit = "kO"
        data = gas.read_all()
        data = data.reducing / 1000
        display_text(variables[5], data, unit)
        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit] 

    # variable = "nh3"
    avg_data = 0
    for i in range(readings):
        unit = "kO"
        data = gas.read_all()
        data = data.nh3 / 1000
        display_text(variables[6], data, unit)
        avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings),2)) + unit] 

    # variable = "pm1"
    avg_data = 0
    for i in range(readings_air):
        unit = "ug/m3"
        try:
            data = pms5003.read()
        except pmsReadTimeoutError:
            logging.warning("Failed to read PMS5003")
        else:
            data = float(data.pm_ug_per_m3(1.0))
            display_text(variables[7], data, unit)
            avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings_air),2)) + unit] 

    # variable = "pm25"
    avg_data = 0
    for i in range(readings_air):
        unit = "ug/m3"
        try:
            data = pms5003.read()
        except pmsReadTimeoutError:
            logging.warning("Failed to read PMS5003")
        else:
            data = float(data.pm_ug_per_m3(2.5))
            display_text(variables[8], data, unit)
            avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings_air),2)) + unit] 

    # variable = "pm10"
    avg_data = 0
    for i in range(readings_air):
        unit = "ug/m3"
        try:
            data = pms5003.read()
        except pmsReadTimeoutError:
            logging.warning("Failed to read PMS5003")
        else:
            data = float(data.pm_ug_per_m3(10))
            display_text(variables[9], data, unit)
            avg_data += data
        time.sleep(delay)
    output += [str(round((avg_data / readings_air),2)) + unit] 

    st7735.command(ST7735.ST7735_DISPOFF) 

    filename = write_to_file(list(zip(variables,output)))
    copy_file(filename)
    write_to_s3(filename)
    

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
