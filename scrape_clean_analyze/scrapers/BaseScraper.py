import csv, os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from ..utils.helpers import get_random_user_agent


class BaseScraper(ABC):
    def __init__(self):
        self.headers = ['url', 'city', 'price', 'price_per_sqm', 'description', 'district_name',
                        'street_address', 'area_m2', 'bedrooms', 'floor', 'upload_date']
        self.main_url = ''
        self.city_id_dict = None
        self.number_of_pages_to_scrape = None
        self.raw_apartments_csv_path = ''

    @abstractmethod
    def get_url(self, id, page):
        raise NotImplementedError("Subclasses must implement get_url function")

    @abstractmethod
    def get_listings(self, driver):
        raise NotImplementedError("Subclasses must implement get_listings function")

    @abstractmethod
    def parse_listing(self, apartment, city_name, page):
        raise NotImplementedError("Subclasses must implement parse_listing function")

    def scraper(self):
        driver = self.configure_driver()
        data = []

        for city_name, city_id in self.city_id_dict.items():
            for page in range(1, self.number_of_pages_to_scrape + 1):
                driver.get(self.get_url(city_id, page))
                print(f"{self.main_url} - City: {city_name}, Page: {page}")

                listings = self.get_listings(driver)
                if not listings:
                    print(f"{self.main_url} - Skipping Page: {page} — Failed to load listings")
                    continue

                for a in listings:
                    try:
                        record = self.parse_listing(a, city_name, page)
                        if record:
                            data.append(record)
                    except StaleElementReferenceException:
                        self.skip_listing_message(city_name, page, "stale")
                    except Exception as e:
                        self.skip_listing_message(city_name, page, str(e))

        self.write_to_csv(data)
        driver.quit()

    def skip_listing_message(self, city_name, page_counter, error_msg=''):
        print(f"{self.main_url} - {city_name} - Page: {page_counter}: Skipping Listing: {error_msg}")

    def configure_driver(self):
        os.environ["SE_DRIVER_MIRROR_URL"] = "https://msedgedriver.microsoft.com"

        options = EdgeOptions()

        # Headless & window
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

        # Disable images, fonts, media
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2,
            "profile.managed_default_content_settings.javascript": 1,  # keep JS enabled
            "profile.managed_default_content_settings.media": 2,
        }
        options.add_experimental_option("prefs", prefs)

        # Anti-detection (minimal)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Performance flags
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # User agent
        options.add_argument(f"--user-agent={get_random_user_agent()}")

        return webdriver.Edge(options=options)

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
                matched = []

                try:
                    anchors = d.find_elements(By.CSS_SELECTOR, selector)
                except StaleElementReferenceException:
                    return False

                for a in anchors:
                    try:
                        href = a.get_attribute("href")
                        if href and (self.main_url + substr) in href:
                            matched.append(a)
                    except StaleElementReferenceException:
                        continue  # Skip stale element safely

                if len(matched) >= min_count:
                    condition.matched_elements = matched
                    return True

                return False

            WebDriverWait(driver, timeout, poll_frequency=0.5).until(condition)
            return condition.matched_elements

        except TimeoutException:
            print(f"{self.main_url} - Failed: to load {min_count} <a> tags for '{substr}' within {timeout}s")
            return []

    def write_to_csv(self, data):
        """ Writes the list of dictionaries' data to a csv file """
        if data:
            with open(self.raw_apartments_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(data)

            print(f"{self.main_url} - Data written to '{self.raw_apartments_csv_path}'")

        else:
            print(f"{self.main_url} - No data to write.")
