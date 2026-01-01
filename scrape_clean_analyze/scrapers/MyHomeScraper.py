import pandas as pd
from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class MyHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://www.myhome.ge/"
        self.city_id_dict = {'თბილისი': 1, "ქუთაისი": 96, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 5
        self.raw_apartments_csv_path = '../data_output/myhome_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://www.myhome.ge/s/?CardView=1&real_estate_types=1&cities={id}&page={page}'

    def get_listings(self, driver):
        return self.wait_for_links(driver, 'pr')

    def parse_listing(self, apartment, city_name, page):
        try:
            # Wait up to 5 seconds to return 5 div elements
            WebDriverWait(apartment, 1).until(
                lambda _: len(apartment.find_elements(By.XPATH, "./div[2]/div")) > 4
            )
            data_div = apartment.find_elements(By.XPATH, "./div[2]/div")

        except TimeoutException:
            self.skip_listing_message(city_name, page, 'expected 5 div elements to load.')
            return None

        # The div 0 contains data about price and price_per_sqm
        price_data = data_div[0].text.splitlines()
        price = price_data[0] if price_data else pd.NA
        price_per_sqm = price_data[2] if len(price_data) > 2 and 'მ²' in price_data[2] else pd.NA

        # The div 1 contains data about the description
        description_text = data_div[1].text.strip()
        description = description_text if description_text else pd.NA

        # The div 2 contains data about the street address
        street_address_text = data_div[2].text.strip()
        street_address = street_address_text if street_address_text else pd.NA

        # The div 3 contains data about the area_m2 and floor
        area_floor_data = data_div[3].text.splitlines()
        area_m2 = area_floor_data[-2] if len(area_floor_data) > 1 and area_floor_data[-1] == 'მ²' else pd.NA
        floor = area_floor_data[0] if area_floor_data else pd.NA

        # The div 4 contains data about the district_name and upload_date
        district_upload_data = data_div[4].text.splitlines()
        district_name = district_upload_data[0] if district_upload_data else pd.NA
        upload_date = district_upload_data[1] if len(district_upload_data) > 1 else pd.NA

        if pd.isna(price) or pd.isna(district_name) or pd.isna(upload_date):
            self.skip_listing_message(city_name, page, 'Data is not given')
            return None

        return {
                'url': apartment.get_attribute('href'),
                'city': city_name,
                'price': price,
                'price_per_sqm': price_per_sqm,
                'description': description,
                'district_name': district_name,
                'street_address': street_address,
                'area_m2': area_m2,
                'bedrooms': pd.NA,
                'floor': floor,
                'upload_date': upload_date
            }
