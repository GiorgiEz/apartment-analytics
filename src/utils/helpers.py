import requests


def get_usd_exchange_rate():
    response = requests.get("https://api.exchangerate-api.com/v4/latest/GEL")
    data = response.json()
    return data['rates']['USD']
