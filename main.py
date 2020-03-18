import json
import pandas as pd
import requests

from jinja2 import Environment, FileSystemLoader, select_autoescape


class Meteo:
    def __init__(self):
        """Class for meteorological data collection
        """
        self.cities = pd.read_csv(
            'https://worldweather.wmo.int/en/json/full_city_list.txt',
            sep=';'
        )
        self.cities = self.cities[~self.cities.CityId.isna()]
        self.cities.CityId = self.cities.CityId.astype(int)

    def get_city_info(self, city_name: str):
        """For a given city name, return dictionary with downloaded JSON data
        for this city

        :param str city_name: Name of the city to get information for.
        :return: Dictionary with meteorological information for requested city.
        :rtype: dict
        """
        city_id = self.cities.loc[
            self.cities.City == city_name.capitalize(),
            'CityId'
        ].iloc[0]

        # Try until successful
        fetch_successful = False
        while not fetch_successful:
            try:
                city_data = json.loads(requests.get('http://worldweather.wmo.int/en/json/{:d}_en.xml'.format(city_id)).text)['city']
                fetch_successful = True
            except (TimeoutError, requests.exceptions.ConnectionError):
                continue

        return city_data


meteo = Meteo()
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html'])
)
template = env.get_template('mail_template.html')


def prepare_email(cities):
    cities_info = []
    for city in cities:
        cities_info.append(meteo.get_city_info(city))

    mail = template.render(cities_info=cities_info)
    print(mail)
    return mail
