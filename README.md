# air-quality-sensor
air quality sensor - RPi + arduino

# Components
- 10W solar panel
- 4x18650 battery shield + charger
- Arduino nano
- 2x small buttons
- 1x big red button 🛑
- Raspberry Pi zero WH
- Enviro+ sensor
- PMS5003 fine particle sensor

# How it works?
Arduino will schedule a start&stop program for the RPI  
The nano board implements deep sleep so the energy consumption will be pretty low  
No servo chosen due to passive current consumption  
No MOSFET used as a switch because it's not a 🛑Red Button  
2 Buttons used to adjust DC motor position for the 🛑Red Button 

# Schematics

![image](switch_bb.jpg)
![image](full_img.jpg)
