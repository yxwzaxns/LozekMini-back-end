import requests
from app.config import WEATHER_KEY

# key aa4171e9d5a340a488137acfdd036805
#
# https://free-api.heweather.com
#
# https://free-api.heweather.com/s6/weather/now?
#
# https://free-api.heweather.com/s6/weather/now?location=桂林&key=aa4171e9d5a340a488137acfdd036805
#
#
# res = requests.get().json()
def getWeather(location):
    # data = {'location':'guilin','key':WEATHER_KEY}
    url = 'https://free-api.heweather.com/s6/weather/now?key={}&location={}'.format(WEATHER_KEY,location)
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return res.reason

def queryWord(word):
    key = 'ecbdd726d9ecad0c'
    url = 'http://api.jisuapi.com/cidian/word?appkey={}&word={}'.format(key,word)
    print(url)
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return res.reason

def getLocationInfo(lat,lng):
    location = '{},{}'.format(str(lat),str(lng))
    key =  '442acd32ee7f4f6f57fd28abeafad152'
    url = 'http://api.map.baidu.com/geocoder/v2/?location={}&output=json&ak={}'.format(location,key)
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return res.reason
