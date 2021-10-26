## Watcher script
- it detects changes to the to_upload folder and pushes the data to ThingsSpeaks
- the file is cleared afterward

### Service file location
/lib/systemd/system/sensor_upload.service

### Enabling the service
sudo systemctl enable sensor_upload.service          
