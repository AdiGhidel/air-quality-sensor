#!/bin/bash
while inotifywait -e create -r /home/pi/sensor_data/to_upload;
	do /usr/bin/python3 /home/pi/sensor_data/thingsSpeak.py; rm /home/pi/sensor_data/to_upload/data.txt; 
done
