import re
import json

from Modalities.take_photo import take_photo
from Modalities.play_music import play_music
from Modalities.now_time import now_time
from Modalities.open_door import open_door
from Modalities.open_explorer import open_explorer
from Modalities.open_map import open_map
from Modalities.set_alarm import set_alarm
from Modalities.check_downloads import check_downloads
from Modalities.send_email import send_email
from Modalities.turn_on_lamp import turn_on_lamp

class tools_agent:
    def __init__(self):
        

        self.function_call_keywords = [
            {
                "api_name": "check_weather",
                "description": "Automatically get the latest weather information from BMKG",
                "parameters": ["location"],
                "parameters_desc": ["Specified the location. By default is current location"]
            },
            {
                "api_name": "take_photo",
                "description": "Automatically open Windows Camera",
                "parameters": ["camera_id"],
                "parameters_desc": ["Set the camera ID. By default use 0"]
            },
            {
                "api_name": "open_explorer",
                "description": "Automatically open Windows Explorer",
                "parameters": ["path"],
                "parameters_desc": ["Specified the path location. By default is None"]
            },
            {
                "api_name": "open_email",
                "description": "Automatically open Google Mail",
                "parameters": [""],
                "parameters_desc": ["Nothing"]
            },
            {
                "api_name": "open_map",
                "description": "Automatically open Google Maps",
                "parameters": [""],
                "parameters_desc": ["Nothing"]
            },
            {
                "api_name": "open_music",
                "description": "Automatically open Spotfiy",
                "parameters": [""],
                "parameters_desc": ["Nothing"]
            },
            {
                "api_name": "now_time",
                "description": "Get the current time",
                "parameters": [""],
                "parameters_desc": ["Nothing"]
            },
            
            # ... [Additional functions can be added following the same structure]
        ]

        # Extracting function names and descriptions for the prompt
        self.function_descriptions = ''.join(['* {"use_func" : true, "api_name" : '+ func["api_name"] + '", description : "'+ func["description"] + '}\n' for func in self.function_call_keywords])

        #print(self.function_call_keywords)

        self.system_prompt_en = f"""
As your AI assistant, I am programmed to assist in a helpful, respectful, and honest manner. My capabilities include accurately answering questions and utilizing predefined API calls when beneficial. If a user's request warrants an API call, I will provide the API call format:

{{"use_func": true, "api_name": "selected_function"}}

I will suggest an API call only when it's relevant to the user's request. For a list of available API functions and their descriptions, I can call:

{self.function_descriptions}

My goal is to assist users safely and responsibly, ensuring a positive and enriching experience."""
        
        self.system_prompt_id = f"""
Sebagai asisten AI Anda, saya diprogram untuk membantu dengan cara yang bermanfaat, hormat, dan jujur. Saya mampu menjawab pertanyaan dengan akurat dan menggunakan panggilan API yang sudah ditentukan jika bermanfaat. Jika permintaan pengguna memerlukan panggilan API, saya akan menyediakan format panggilan API:

{{"use_func": true, "api_name": "selected_function"}}

Saya hanya akan menyarankan panggilan API jika relevan dengan permintaan pengguna. Untuk daftar fungsi API yang tersedia dan deskripsinya, saya dapat memanggil:

{self.function_descriptions}

Tujuan saya adalah untuk membantu pengguna dengan cara yang aman dan bertanggung jawab, memastikan pengalaman yang positif dan memperkaya. Semua respons saya akan diberikan dalam bahasa Indonesia.
"""
        self.model_temperature = 0.7

    def func_call_parser(self, output_text):
        json_output = None
        is_func = False
        try:
            # Using regular expression to find JSON object in the output text
            match = re.search(r'\{.*?\}', output_text)
            if match:
                json_str = match.group()
                json_output = json.loads(json_str)
                if json_output.get("use_func") == True:
                    is_func = True

            else:
                # No JSON output found in the response
                pass

        except json.JSONDecodeError as e:
            #print("Error decoding JSON:", e)
            is_func = True
            json_output = {"error": str(e), "request": output_text}

        except Exception as e:
            #print("An error occurred:", e)
            json_output = {"error": str(e), "request": output_text}
            is_func = True
            
        return json_output, is_func

    def function_calling(self, json_output, weather_agent):
        output = ""
        try:
            output = f'No function call named {json_output["api_name"]}'

            if(("check_weather" in json_output["api_name"])):
                weather_reports = []
                for location_data in weather_agent["weather_data"]:
                    location = location_data["location"]
                    temperature = location_data["temperature"]
                    unit = location_data['unit']
                    condition = location_data["condition"]
                    weather_reports.append(f"{location}: {temperature}{unit} with {condition} condition")

                # Format the entire message
                weather_data_str = '; '.join(weather_reports)
                last_message = (
                    f"Current Location: Bojongsoang, Dayeuhkolot, Bandung Regency, West Java\n"
                    f"Weather Data: {weather_data_str}\n"
                    f"Bandung Regency Average Temperature: {weather_agent['average_temp']}\n"
                    f"Last Updated: {weather_agent['last_updated']}\n"
                    f"Source: {weather_agent['source']}"
        )
                output = last_message
                
            elif(("take_photo" in json_output["api_name"])):
                output = take_photo()

            elif("open_door" in json_output["api_name"]):
                output = open_door()

            elif("turn_on_lamp" in json_output["api_name"]):
                output = turn_on_lamp()

            elif(("open_music" in json_output["api_name"])):
                output = play_music()

            elif(("now_time" in json_output["api_name"])):
                output = now_time()    
            
            elif(("open_map" in json_output["api_name"])):
                output = open_map()
                
            elif(("open_explorer" in json_output["api_name"])):
                output = open_explorer()
                
            elif(("open_downloads" in json_output["api_name"])):
                output = check_downloads()
                
            elif("open_alarm" in json_output["api_name"]):
                output = set_alarm()
                
            elif(("open_email" in json_output["api_name"])):
                output = send_email()
            
        except Exception as e:
            if(("check_weather" in str(json_output))):
                output = str(weather_agent)
                
            elif(("take_photo" in str(json_output))):
                output = take_photo()

            elif("open_door" in str(json_output)):
                output = open_door()

            elif("turn_on_lamp" in str(json_output)):
                output = turn_on_lamp()

            elif(("open_music" in str(json_output))):
                output = play_music()

            elif(("now_time" in str(json_output))):
                output = now_time()    
            
            elif(("open_map" in str(json_output))):
                output = open_map()
                
            elif(("open_explorer" in str(json_output))):
                output = open_explorer()
                
            elif(("open_downloads" in str(json_output))):
                output = check_downloads()
                
            elif("open_alarm" in str(json_output)):
                output = set_alarm()
                
            elif(("open_music" in str(json_output))):
                output = send_email()
        
        return output
