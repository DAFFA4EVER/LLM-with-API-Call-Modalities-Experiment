import requests
from bs4 import BeautifulSoup
from datetime import datetime

# URLs for different locations
default_url = {
    "Bandung": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kota=Bandung&AreaID=501212&Prov=35",
    "Lembang": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Lembang&kab=Kab._Bandung_Barat&Prov=Jawa_Barat&AreaID=501599",
    "Dayeuh Kolot": "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Dayeuhkolot&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009460",
    "Bojongsoang" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Bojongsoang&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009283",
    "Cihampelas" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Cihampelas&kab=Kab._Bandung_Barat&Prov=Jawa_Barat&AreaID=5009353",
    "Pangalengan" : "https://www.bmkg.go.id/cuaca/prakiraan-cuaca.bmkg?Kec=Pangalengan&kab=Kab._Bandung&Prov=Jawa_Barat&AreaID=5009655"
}

def get_temperature(location):
    # Check if the location is in the URL dictionary
    try:
        if location in default_url:
            # Get the URL for the specified location
            url = default_url[location]
            # Set the headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            

            # Find the image tag with the specified path in 'src'
            weather_icon_tag = soup.find('img', src=lambda x: x and "/asset/img/weather_icon" in x)
            condition = "Condition not found"
            if weather_icon_tag and weather_icon_tag.find_next_sibling('p'):
                condition = weather_icon_tag.find_next_sibling('p').get_text().strip()
            
            temperature_element = soup.find('h2', class_='heading-md')
            temperature = temperature_element.get_text().replace('°C', '').strip() if temperature_element else "Temperature not found"

            # Get the current datetime
            now = datetime.now()

            # Format the datetime object to the desired format: Day Month Year HH:MM
            formatted_datetime = now.strftime("%d %B %Y %H:%M")

            return {"location": location, "temperature" : int(temperature), 'unit' : '°C', "condition" : condition, "last_updated" : formatted_datetime}
        else:
            return "Invalid location", "Condition not found"
    except Exception as e:
        print(e)

# Function to get the temperatures and conditions of all locations
def get_all_temperatures(urls=default_url):
    all_weather_data = []
    for location in urls.keys():
        all_weather_data.append(get_temperature(location))
    return all_weather_data
