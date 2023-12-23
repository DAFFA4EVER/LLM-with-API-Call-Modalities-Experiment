import paho.mqtt.client as mqtt
import json

class WeatherSubscriber:
    def __init__(self):
        self.cache = []  # Cache to store the last 10 messages
        self.last_messages = {}
        self.client = mqtt.Client("Subscriber")
        self.client.on_message = self.on_message
        self.broker_address = "localhost"

    def on_message(self, client, userdata, message):
        if(len(self.cache) == 0):
            print("- (Subscriber) : Connecting to broker")

        payload = message.payload.decode('utf-8')
        try:
            location_data = json.loads(payload)
            if(len(self.cache) == 0):
                print("- (Subscriber) : First data received succesfully")
            self.update_cache(location_data)
            self.process_cache()
        except json.JSONDecodeError:
            print("- (Subscriber) : Error decoding JSON")
        except KeyError:
            print("- (Subscriber) : Received data is missing expected fields")

    def update_cache(self, location_data):
        # Check if location is already in the cache and update it
        for i, data in enumerate(self.cache):
            if data['location'] == location_data['location']:
                self.cache[i] = location_data
                return
        
        # Add new location data to the cache
        self.cache.append(location_data)
        # Keep only the last 10 messages in the cache
        if len(self.cache) > 10:
            self.cache.pop(0)

    def process_cache(self):
        # Check if all last updated times are the same
        last_updated_times = set(data['last_updated'] for data in self.cache)
        if len(last_updated_times) == 1:
            avg_temperature = sum(data['temperature'] for data in self.cache) / len(self.cache)
            # Since all last_updated times are the same, take it from any entry in the cache
            last_updated = next(iter(self.cache))['last_updated']
            self.last_messages = {
                "weather_data": self.cache,
                "average_temp": f"{avg_temperature:.2f} °C",
                "source": "https://www.bmkg.go.id/",
                "last_updated": last_updated,
            }
        else:
            self.last_messages = {
                "weather_data": self.cache,
                "average_temp": "Cannot calculate average temperature - times differ.",
                "source": "https://www.bmkg.go.id/",
                "last_updated": "Data times differ"
            }

        

    def get_message(self):
        return self.last_messages

    def start_subscribe(self):
        self.client.connect(self.broker_address, port=3333)
        self.client.loop_start()
        self.client.subscribe("temperatures")
    
    def stop_subscribe(self):
        self.client.loop_stop()
