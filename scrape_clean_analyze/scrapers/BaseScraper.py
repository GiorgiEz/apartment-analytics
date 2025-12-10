import csv, winreg, os
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from ..utils.helpers import get_random_user_agent


class BaseScraper:
    def __init__(self):
        self.headers = ['url', 'city', 'price', 'price_per_sqm', 'description', 'district_name',
                        'street_address', 'area_m2', 'bedrooms', 'floor', 'upload_date']
        self.raw_apartments_csv_path = ''
        self.main_url = ''

    def scraper(self):
        raise NotImplementedError("Subclasses must implement scraper function")

    def configure_driver(self):
        os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"

        options = EdgeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f"--user-agent={get_random_user_agent()}")

        driver = webdriver.Edge(options=options)
        return driver

    def safe_find_element(self, driver, by, value, timeout=1):
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            return None

    def wait_for_links(self, driver, substr, min_count=10, selector='a', timeout=3):
        """
        Waits until at least `min_count` <a> tags are found where href contains `substr`.
        Returns the list of matching elements if successful, otherwise an empty list.
        """
        try:
            def condition(d):
                elements = [
                    a for a in d.find_elements(By.CSS_SELECTOR, selector)
                    if self.main_url + substr in str(a.get_attribute('href'))
                ]
                # Store as attribute to retrieve later if successful
                if len(elements) >= min_count:
                    condition.matched_elements = elements
                    return True
                return False

            WebDriverWait(driver, timeout).until(condition)
            return condition.matched_elements  # Already found, safe to return
        except TimeoutException:
            print(f"{self.main_url} - Failed: to load at least {min_count} <a> tags for '{substr}' within {timeout}s")
            return []

    def write_to_csv(self, data):
        """ Writes the list of dictionaries' data to a csv file """
        if not data:
            print(f"{self.main_url} - No data to write.")
            return

        with open(self.raw_apartments_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(data)

        print(f"{self.main_url} - Data written to '{self.raw_apartments_csv_path}'")
