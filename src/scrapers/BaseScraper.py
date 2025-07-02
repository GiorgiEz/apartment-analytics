import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager



class BaseScraper:
    def __init__(self):
        self.user_agent = ("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                           "HeadlessBrowser/1.0 Chrome/90.0.4430.85 Safari/537.36")
        self.headers = ['url', 'city', 'price', 'price_per_sqm', 'description', 'street_name',
                        'street_number', 'area_m2', 'upload_date']
        self.raw_apartments_csv_path = 'data_output/raw_apartments.csv'

    def configure_chromedriver(self):
        """ Configures the chromedriver and initializes the driver """
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--headless')  # uncomment for headless mode
        options.add_argument('--disable-blink-features=AutomationControlled')  # avoid detection
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument(self.user_agent)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.notifications": 2,
        }
        options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def write_to_csv(self, data):
        """ Writes the list of dictionaries' data to a csv file """
        if not data:
            print("No data to write.")
            return

        with open(self.raw_apartments_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data written to '{self.raw_apartments_csv_path}'")
