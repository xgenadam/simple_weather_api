import os
import requests

from collections import Counter
from itertools import chain


class OpenWeatherAPIException(Exception):
    pass


def get_relevant_daily_data(daily_data):

    min_temp = daily_data['temp']['min']
    max_temp = daily_data['temp']['max']
    weather = [w['main'] for w in daily_data['weather']]

    return {'min_temp': min_temp, 'max_temp': max_temp, 'weather': weather}


def fortnight_forecast(city_name):

    api_key = os.environ.get('OPENWEATHER_API_KEY')
    url = 'https://api.openweathermap.org/data/2.5/forecast/daily'

    params = {
        'q': city_name,
        'cnt': 14,
        'mode': 'json',
        'APPID': api_key,
        'units': 'metric'
    }

    response = requests.get(url=url, params=params)

    if response.status_code != 200:
        raise OpenWeatherAPIException

    data = response.json()
    try:
        relevant_data = [get_relevant_daily_data(daily_data)
                         for daily_data in data['list']]

        max_temp = max([item['max_temp'] for item in relevant_data])
        min_temp = min([item['min_temp'] for item in relevant_data])
        nested_weather_list = [item['weather'] for item in relevant_data]

        weather_occurences = Counter(chain(*nested_weather_list))
        most_likely_weather = sorted(weather_occurences,
                                     key=lambda t: t[1],
                                     reverse=True)[0]

        return {'max_temp': max_temp, 'min_temp': min_temp, 'most_likely_weather': str(most_likely_weather)}

    except KeyError:
        raise OpenWeatherAPIException

    except IndexError:
        raise OpenWeatherAPIException


if __name__ == '__main__':
    london_forecast = fortnight_forecast('London')
    print('Most likely London weather for next '
          'two weeks: {most_likely_weather}\n'
          'max temperature: {max_temp}\n'
          'min temperature: {min_temp}'.format(**london_forecast))