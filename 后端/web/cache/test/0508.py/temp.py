import requests

def get_weather(city):
    api_key = 'your_api_key_here'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url).json()
    if response['cod'] == 200:
        print(f"Weather in {city}: {response['weather'][0]['description']}, Temp: {response['main']['temp']}K")
    else:
        print(f"City not found!")


get_weather('London')