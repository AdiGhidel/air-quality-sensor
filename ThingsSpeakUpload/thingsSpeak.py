import thingspeak, collections

device = thingspeak.Channel('****', api_key='****')
fields = ["temperature", "pressure", "humidity", "reduced", "nh3", "pm1", "pm25", "pm10"]

def getDigits(valUnit: str):
    crt = ""
    for c in valUnit:
        if c.isdigit() or c == ".":
            crt += c
    return crt

with open('/home/pi/sensor_data/to_upload/data.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    data = [getDigits(d.split(":")[1].strip()) for d in lines if any(word in d for word in fields)]

    values = dict()
    for i, el in enumerate(data):
        values[i + 1] = el
    if len(values) != 8:
        print("wrong no of parameters")
        exit(1)

    try:
        device.update(values)
    except Exception as e:
        print(f"Data {data} failed to upload")
    

