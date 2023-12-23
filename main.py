from llm_pipeline import llm_pipeline
from tools_agent import tools_agent
from chat_management import chat_management
from token_management import get_total_token, chat_summary
from get_model_output import get_model_output
import subprocess
import asyncio
import concurrent.futures
import time
from Modalities.Bandung_Weather.bandung_weather_subscriber import WeatherSubscriber
import json

chat_continue = True
model_preprompt = "Hello, what can I help with?"
user_input = ""

stream_output = True

cached_chat = []

max_tokens = 4096

current_token = 0

print("- (LLM) : Connecting to modalitites API")
# Start the Bandung Weather Publisher
bandung_publisher_path = "Modalities/Bandung_Weather/bandung_weather_publisher.py"
command = f"python {bandung_publisher_path}"
publisher_process = subprocess.Popen(command, shell=True)

weather_agent = WeatherSubscriber()

weather_message = []

weather_agent.start_subscribe()

async def append_weather_message(weather_agent, weather_message):
    loop = asyncio.get_running_loop()
    await asyncio.sleep(5)  # Adjust this duration as needed

    with concurrent.futures.ThreadPoolExecutor() as pool:
        while not weather_agent.get_message():
            await asyncio.sleep(1)  # Check every second

        message = await loop.run_in_executor(pool, weather_agent.get_message)
        if(len(weather_message) == 0):
            print("- (LLM) : Connected to weather API")

        weather_message.append(message)

# Running the asynchronous function
asyncio.run(append_weather_message(weather_agent, weather_message))

initial = True

total_token = 0

chats_list = []

set_language = 'en'

normal_prompt_en = "You are an advanced AI assistant designed to answer user queries accurately and helpfully. Your responses should be informative, clear, and relevant to the questions asked. Focus on understanding the user's intent and provide detailed, well-researched answers. If a query is ambiguous or lacks specific details, seek clarification to ensure your response is as helpful as possible. Remember to maintain a polite and professional tone at all times. Your goal is to assist users by providing accurate information, practical advice, or solutions to their problems based on the information available."

normal_prompt_id = "Anda adalah asisten AI canggih yang dirancang untuk menjawab pertanyaan pengguna secara akurat dan bermanfaat. Tanggapan Anda harus informatif, jelas, dan relevan dengan pertanyaan yang diajukan. Fokus pada pemahaman maksud pengguna dan berikan jawaban yang mendetail dan telah diteliti dengan baik. Jika pertanyaannya ambigu atau tidak memiliki detail spesifik, mintalah klarifikasi untuk memastikan jawaban Anda berguna. Ingatlah untuk selalu menjaga nada bicara yang sopan dan profesional. Tujuan Anda adalah membantu pengguna dengan memberikan informasi akurat, saran praktis, atau solusi terhadap masalah mereka berdasarkan informasi yang tersedia."

agent_tools =  tools_agent()

if(set_language == 'id'):
    print("- (LLM) : LLM language set to Indonesian (ALPHA)")
    agent_tools_prompt = agent_tools.system_prompt_id
    normal_prompt = normal_prompt_id
else:
    print("- (LLM) : LLM language set to English")
    agent_tools_prompt = agent_tools.system_prompt_en
    normal_prompt = normal_prompt_en

try:
    while(chat_continue):
        if(weather_message[-1] != {}):
            if(initial):
                initial = False
                time.sleep(5)
                print("- (LLM) : LLM received the first weather data")
                print("\n\n(Assistant)\nHi! What can I help?")

            user_input = input("\n(You)\n")
            print(f"\n(Assistant)")
            # [Tools Agent]
            current_agent = "tools"
            model_response, current_token = llm_pipeline(user_input=user_input, system_prompt=normal_prompt, agent_tools_prompt=agent_tools_prompt, agent=current_agent, assistant_prompt='', temperature=agent_tools.model_temperature, max_tokens=-1, chats_list=chats_list, stream_output=stream_output)
            
            total_token += current_token

            is_func = False
            func_call = None

            if(current_agent == "tools"):
                func_call_json, is_func = agent_tools.func_call_parser(model_response)

            if(is_func):
                func_call_json["api_response"] = agent_tools.function_calling(func_call_json, weather_agent=weather_message[-1])
                if(func_call_json["api_response"] != "waiting"):
                    chats_list = chat_management(user_input=user_input, model_output=model_response, chat_list=chats_list, mode="tools", system_output=func_call_json["api_response"])
                else:
                    is_func = False
                    chats_list = chat_management(user_input=user_input, model_output=model_response, chat_list=chats_list, mode="tools", system_output=func_call_json)

            # [Normal Agent]
            if(is_func):
                model_response, current_token = llm_pipeline(user_input=user_input, system_prompt=normal_prompt, agent_tools_prompt=agent_tools_prompt, agent="tools_return", assistant_prompt=func_call_json["api_response"], temperature=0.5, max_tokens=-1, chats_list=chats_list, stream_output=stream_output)
                
                total_token += current_token

                chats_list = chat_management(user_input=user_input, model_output=model_response, chat_list=chats_list, mode="normal", system_output=func_call_json)


            else:
                chats_list = chat_management(user_input=user_input, model_output=model_response, chat_list=chats_list, mode="normal", system_output="")

            # To give gap
            if(stream_output):
                print()

            chat_continue = input("\nContinue to chat?(Yes/No) ")

            print(f"Approximate tokens used : {total_token}")
            if(len(weather_message) > 2):
                weather_message.pop(0)

            is_func = False
            if(chat_continue.lower() == "yes"):
                chat_continue = True
                if(total_token >= max_tokens):
                    print("Warning! Current tokens exceding the limit. Performing chat summarization. Please wait...🔃")
                    model_response, total_token = llm_pipeline(user_input=user_input, system_prompt=normal_prompt, agent_tools_prompt=agent_tools_prompt, agent="summarize", assistant_prompt=func_call_json, temperature=0.7, max_tokens=-1, chats_list=chats_list, stream_output=stream_output)

                    chats_list, cached_chat = chat_summary(chats_list=chats_list, chat_summary=model_response, cached_chat=cached_chat)
            else:
                # Safely terminate the process
                publisher_process.terminate()
                try:
                    # Wait for the process to end, giving it a chance to clean up if necessary
                    publisher_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate within the timeout
                    publisher_process.kill()
                chat_continue = False    
                for chat in chats_list:
                    print(chat)
                    print("")
        else:
            time.sleep(1)

except KeyboardInterrupt:
    # Graceful termination on keyboard interrupt
    publisher_process.terminate()
    weather_agent.stop_subscribe()
    try:
        publisher_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        publisher_process.kill()

finally:
    weather_agent.stop_subscribe()
    # Ensure the process is terminated in the end
    if publisher_process.poll() is None:  # Check if the process is still running
        publisher_process.terminate()
        try:
            publisher_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            publisher_process.kill()