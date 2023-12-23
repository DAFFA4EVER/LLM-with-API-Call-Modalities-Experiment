import paho.mqtt.client as mqtt
import time
import subprocess
import threading
from weather_scrapping import get_all_temperatures, get_temperature  # Assuming get_all_temperatures is defined in weather_scrapping
import json
# Command to run Mosquitto broker with a specified port
mosquitto_path = r"C:\Program Files\mosquitto\mosquitto.exe"
command = f'"{mosquitto_path}" -p 3333'
process = subprocess.Popen(command, shell=True)

urls = {
    "Bandung": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kota=Bandung&AreaID=501212&Prov=35",
    "Lembang": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Lembang&kab=Kab._Bandung_Barat&Prov=Jawa_Barat&AreaID=501599",
    "Dayeuh Kolot": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Dayeuhkolot&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009460",
    "Bojongsoang" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Bojongsoang&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009283",
    "Cihampelas" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Cihampelas&kab=Kab._Bandung_Barat&Prov=Jawa_Barat&AreaID=5009353",
    "Pangalengan" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Pangalengan&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009655"
}

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    print("- (Publisher) : Connected with result code", str(rc))

# Initialize MQTT Client
print("- (Publisher) : Creating a new instance")
client = mqtt.Client("Publisher")
client.on_connect = on_connect

# Connect to MQTT Broker
print("- (Publisher) : Connecting to broker")
broker_address = "localhost"  # public broker
client.connect(broker_address, port=3333)
client.loop_start()

# Function to publish temperature for a specific location
def publish_single_temperature(client, location):
    temperature_data = get_temperature(location)
    if isinstance(temperature_data, dict):
        temperature_json = json.dumps(temperature_data)
        #print(temperature_json)
        client.publish(f"temperatures", temperature_json)

# Thread function to handle each location
def location_thread(location):
    print(f"- (Publisher) : Starting thread for {location}")
    try:
        while True:
            publish_single_temperature(client, location)
            time.sleep(10)  # Sleep for 10 minutes
    except KeyboardInterrupt:
        pass
    finally:
        print(f"- (Publisher) : Stopping thread for {location}")

# Start a thread for each location
threads = []
for location in urls.keys():
    thread = threading.Thread(target=location_thread, args=(location,))
    threads.append(thread)
    thread.start()