import requests

def main(city, api_key):
    """查询指定城市的天气信息"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    try:
        response = requests.get(url).json()
        if response['cod'] == 200:
            return {
                'city': city,
                'description': response['weather'][0]['description'],
                'temperature': response['main']['temp'],
                'unit': 'K'
            }
        return {'error': f"City '{city}' not found!"}
    except Exception as e:
        return {'error': f"API请求失败: {str(e)}"}

if __name__ == "__main__":
    # 配置API密钥（建议从环境变量读取）
    API_KEY = 'your_api_key_here'  
    
    city = "London"
    
    # 查询并显示结果
    result = main(city, API_KEY)
    if 'error' in result:
        print(f"错误: {result['error']}")
    else:
        print(f"{result['city']}的天气：{result['description']}，温度：{result['temperature']}{result['unit']}")