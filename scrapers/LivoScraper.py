import pandas as pd
from selenium.webdriver.common.by import By
from scrapers.BaseScraper import BaseScraper
from config import paths


class LivoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://livo.ge/"
        self.city_id_dict = {'თბილისი': 1, "ქუთაისი": 96, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 10
        self.raw_apartments_csv_path = paths.LIVO_APARTMENTS_RAW_PATH
        self.month_abbreviations = ['იან', 'თებ', 'მარ', 'აპრ', 'მაი', 'ივნ','ივლ','აგვ', 'სექ', 'ოქტ', 'ნოე', 'დეკ']

    def get_url(self, city_id, page, deal_type):
        """ URL for apartment listings (not including houses, hotels or other real estate types).
            Deal Types 1 - (იყიდება), 2 - (ქირავდება).
            real_estate_types = 1 (ბინა)
        """
        return (f'https://livo.ge/s?deal_types={deal_type}&currency_id=2&real_estate_types=1&cities={city_id}&page={page}&order_by=date&sequence=desc')

    def get_listings(self, driver):
        return self.wait_for_links(driver, 'udzravi-qoneba', selector='a')

    def parse_listing(self, apartment, city_name, page):
        child = apartment.find_element(By.XPATH, './div')  # Get child div of the <a> tag
        divs = child.find_elements(By.XPATH, './div')

        if len(divs) < 2:
            self.skip_listing_message(city_name, page, "Outer Div didn't load")
            return None

        # 1. div for price, price_per_sqm, description, street_address
        inner_div = divs[1].find_elements(By.XPATH, './div')
        if len(inner_div) < 4:
            self.skip_listing_message(city_name, page, "Inner Div didn't load")
            return None

        price_div = inner_div[0].text.strip().split('\n')
        price_parts = [p.strip() for p in price_div if p.strip()]  # ['234,527 ₾', '4,181/მ²', '₾', '$']

        price = price_parts[0]  # '234,527 ₾'
        currency_label = "₾" if "₾" in price else "$"
        price_per_sqm = price_parts[1] + f" {currency_label}"  # '4,181/მ²'

        description = divs[1].find_element(By.XPATH, './span').text.strip()  # იყიდება 3 ოთახიანი ბინა დიდუბეში
        street_address = inner_div[1].text.strip()  # მირიან მეფის ქ.

        area_m2_floor_bedroom = inner_div[2].find_elements(By.XPATH, './div')

        area_m2, floor, bedrooms = pd.NA, pd.NA, pd.NA

        for child_div in area_m2_floor_bedroom:
            txt = child_div.text.strip()

            if 'მ²' in txt:
                area_m2 = txt
                continue

            try:
                path_d = child_div.find_element(By.XPATH, ".//*[name()='svg']//*[name()='path']").get_attribute('d')

                # Bedrooms icon
                if path_d.startswith('M14.118 6.25V3.318'):
                    bedrooms = txt

                # Floor icon
                elif path_d.startswith('M13.134 1C14.164 1'):
                    floor = txt

            except:
                pass

        district_upload_date = inner_div[3].find_elements(By.XPATH, './div')
        district_name = district_upload_date[0].text.strip() if city_name != "თბილისი" else pd.NA  # ვაკე-საბურთალო
        upload_date = district_upload_date[1].text.strip()  # 24 თებ. 19:24

        if pd.isna(price) or pd.isna(street_address) or pd.isna(area_m2):
            self.skip_listing_message(city_name, page, "Data is not given")
            return None

        return {
            'url': apartment.get_attribute('href'),
            'city': city_name,
            'price': price,
            'price_per_sqm': price_per_sqm,
            'description': description,
            'district_name': district_name,
            'street_address': street_address,
            'bedrooms': bedrooms,
            'floor': floor,
            'area_m2': area_m2,
            'upload_date': upload_date
        }
