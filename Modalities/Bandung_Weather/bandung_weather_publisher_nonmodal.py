import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import subprocess
from weather_scrapping import get_all_temperatures  # Assuming get_all_temperatures is defined in weather_scrapping

# Command to run Mosquitto broker with a specified port
mosquitto_path = r"C:\Program Files\mosquitto\mosquitto.exe"
command = f'"{mosquitto_path}" -p 3333'
process = subprocess.Popen(command, shell=True)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", str(rc))

print("Creating a new instance")
client = mqtt.Client("Publisher")
client.on_connect = on_connect

print("Connecting to broker")
broker_address = "localhost"  # public broker
client.connect(broker_address, port=3333)
client.loop_start()

try:
    while True:
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Fetch all temperature data
        temperatures = get_all_temperatures()  # Call to get temperatures for all locations
        
        # Add the last updated time to the data
        #temperatures["last_updated"] = current_time
        
        # Serialize the data to a JSON-formatted string
        temperature_json = json.dumps({"data" : temperatures, "source" : "https://www.bmkg.go.id", "last_updated" : current_time})
        
        # Publish the JSON string to the MQTT topic
        client.publish("temperatures", temperature_json)
        
        # Sleep for 10 minutes
        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    # Clean up the MQTT client and subprocess
    client.loop_stop()
    process.terminate()

def terminate_publisher():
    client.loop_stop()
    process.terminate()
