import pandas as pd
import re
from selenium.webdriver.common.by import By
from scrapers.BaseScraper import BaseScraper
from config import paths


class SSHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://home.ss.ge/ka/udzravi-qoneba/"
        self.city_id_dict = {'თბილისი': 95, "ქუთაისი": 97, 'ბათუმი': 96}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 10
        self.raw_apartments_csv_path = paths.SSHOME_APARTMENTS_RAW_PATH

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://home.ss.ge/ka/udzravi-qoneba/l/bina?cityIdList={id}&order=1&page={page}'

    def get_listings(self, driver):
        try:
            listing_container = self.safe_find_element(driver, By.CLASS_NAME, "listing-container")
            if not listing_container:
                return []

            top_grid_lard = self.safe_find_element(listing_container, By.CLASS_NAME, "top-grid-lard")
            if not top_grid_lard:
                return []

            child_divs = top_grid_lard.find_elements(By.TAG_NAME, "div")
            if not child_divs:
                return []

            grid = child_divs[0]
            return self.wait_for_links(grid, '', selector='a')

        except Exception as e:
            return []

    def parse_listing(self, apartment, city_name, page):
        href = str(apartment.get_attribute('href'))
        if not href or self.main_url not in href:
            self.skip_listing_message(city_name, page, "href didn't load")
            return None

        price_span = self.safe_find_element(apartment, By.CLASS_NAME, 'listing-detailed-item-price')
        price = price_span.text.strip() if price_span else pd.NA

        desc_h2 = self.safe_find_element(apartment, By.CLASS_NAME, 'listing-detailed-item-title')
        description = desc_h2.text.strip() if desc_h2 else pd.NA

        addr_span = self.safe_find_element(apartment, By.CLASS_NAME, 'listing-detailed-item-address')
        street_address = addr_span.text.strip() if addr_span else pd.NA

        area_span = self.safe_find_element(apartment, By.CLASS_NAME, "icon-crop_free")
        area_span_parent = self.safe_find_element(area_span, By.XPATH, './..') if area_span else None
        area_m2 = area_span_parent.text.strip() if area_span_parent else pd.NA

        bedroom_span = self.safe_find_element(apartment, By.CLASS_NAME, "icon-bed")
        bedroom_parent = self.safe_find_element(bedroom_span, By.XPATH, './..') if bedroom_span else None
        bedrooms = bedroom_parent.text.strip() if bedroom_parent else pd.NA

        floor_span = self.safe_find_element(apartment, By.CLASS_NAME, "icon-stairs")
        floor_span_parent = self.safe_find_element(floor_span, By.XPATH, './..') if floor_span else None
        floor = floor_span_parent.text.strip() if floor_span_parent else pd.NA

        create_date = self.safe_find_element(apartment, By.CLASS_NAME, 'create-date')
        upload_date = create_date.text.strip() if create_date else pd.NA

        if pd.isna(price) or not re.search(r"[$₾]", price) or pd.isna(street_address) or pd.isna(area_m2):
            self.skip_listing_message(city_name, page, "Data is not given")
            return None

        return {
            'url': href,
            'city': city_name,
            'price': price,
            'price_per_sqm': pd.NA,
            'description': description,
            'district_name': pd.NA,
            'street_address': street_address,
            'area_m2': area_m2,
            'bedrooms': bedrooms,
            'floor': floor,
            'upload_date': upload_date
        }
