import random, requests, time



def get_random_user_agent():
    """ User agents to use when scraping data """
    user_agents = [
        # Windows - Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",

        # macOS - Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",

        # Windows - Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",

        # Android - Chrome Mobile
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.131 Mobile Safari/537.36",

        # iPhone - Safari Mobile
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",

        # Linux - Chrome
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.184 Safari/537.36",

        # Windows 11 - Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.1823.67 Safari/537.36 Edg/114.0.1823.67",

        # macOS - Chrome
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",

        # Samsung Android - Chrome Mobile
        "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.131 Mobile Safari/537.36",

        # iPad - Safari
        "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    ]

    return random.choice(user_agents)


def get_usd_exchange_rate(retries=3, timeout=3.0, backoff=1.0):
    last_error = None
    EXCHANGE_URL = "https://api.exchangerate-api.com/v4/latest/GEL"

    for attempt in range(retries):
        try:
            response = requests.get(EXCHANGE_URL, timeout=timeout)
            response.raise_for_status()  # raises on 4xx/5xx

            data = response.json()
            return data["rates"]["USD"]

        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError) as e:
            last_error = e

            # do not retry on last attempt
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
            else:
                break

    raise RuntimeError("Failed to fetch USD exchange rate") from last_error

geo_months = {
    'იან': 1, 'თებ': 2, 'მარ': 3, 'აპრ': 4, 'მაი': 5, 'ივნ': 6,
    'ივლ': 7, 'აგვ': 8, 'სექ': 9, 'ოქტ': 10, 'ნოე': 11, 'დეკ': 12
}
