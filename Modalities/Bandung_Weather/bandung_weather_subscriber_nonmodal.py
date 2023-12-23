import paho.mqtt.client as mqtt
import json
# Dictionary to store the last message for each topic
last_messages = {}

# handle received messages
def on_message(client, userdata, message):
    topic = message.topic
    payload = (message.payload.decode("utf-8"))

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return

    last_messages = data

    print(last_messages)

# new client
print("Creating a new instance")
client = mqtt.Client("Subscriber")

# callback function with the client
client.on_message = on_message

# connect broker
print("Connecting to broker")
broker_address = "localhost"  # public broker
client.connect(broker_address, port=3333)

# client loop
client.loop_start()

print("Subscribing to topic", "temperatures")
client.subscribe("temperatures")

# client loop 
try:
    # Run a loop to keep the script active
    while True:
        pass
except KeyboardInterrupt:
    pass
finally:
    # stop the client loop
    client.loop_stop()
