import requests, time


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
