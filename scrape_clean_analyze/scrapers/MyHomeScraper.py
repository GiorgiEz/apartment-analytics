import pandas as pd
from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException


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

    def scraper(self):
        """ Main function to scrape the data from myhome.ge website """
        driver = self.configure_driver()
        apartments_data = []

        for city_name, city_id in self.city_id_dict.items():
            page_counter = 1

            while page_counter <= self.number_of_pages_to_scrape:
                try:
                    driver.get(self.get_url(city_id, page_counter))
                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")

                    apartments = self.wait_for_links(driver, 'pr')
                    if len(apartments) == 0:
                        print(f"Skipping Page: {page_counter} — links not loaded")
                        page_counter += 1
                        continue

                    for a in apartments:
                        try:
                            # Wait up to 5 seconds to return 5 div elements
                            WebDriverWait(a, 1).until(
                                lambda driver: len(a.find_elements(By.XPATH, "./div[2]/div")) > 4
                            )
                            data_div_info = a.find_elements(By.XPATH, "./div[2]/div")

                        except TimeoutException:
                            print(f"{self.main_url} - Skipping this listing — expected 5 div elements to load.")
                            continue

                        # The div 0 contains data about price and price_per_sqm
                        price_data = data_div_info[0].text.splitlines()
                        price = price_data[0] if len(price_data) > 0 else pd.NA
                        price_per_sqm = price_data[2] if len(price_data) > 2 and 'მ²' in price_data[2] else pd.NA

                        # The div 1 contains data about the description
                        description = data_div_info[1].text if data_div_info[1].text else pd.NA

                        # The div 2 contains data about the street address
                        street_address = data_div_info[2].text if data_div_info[2].text else pd.NA

                        # The div 3 contains data about the area_m2 and floor
                        area_floor_data = data_div_info[3].text.splitlines()
                        area_m2 = area_floor_data[-2] if len(area_floor_data) > 1 and area_floor_data[-1] == 'მ²' else pd.NA
                        floor = area_floor_data[0] if len(area_floor_data) > 0 else pd.NA

                        # The div 4 contains data about the district_name and upload_date
                        district_upload_data = data_div_info[4].text.splitlines()
                        district_name = district_upload_data[0] if len(district_upload_data) > 0 else pd.NA
                        upload_date = district_upload_data[1] if len(district_upload_data) > 1 else pd.NA

                        if pd.isna(price) or pd.isna(district_name) or pd.isna(upload_date):
                            continue

                        apartments_data.append({
                            'url': a.get_attribute('href'),
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
                        })


                except StaleElementReferenceException:
                    print(f"{self.main_url} - Skipping Page... due to stale element error: "
                          f"{city_name}, Page: {page_counter}")

                except Exception as parse_err:
                    print(f"{self.main_url} - Skipping Page... due to Error: {parse_err}")

                finally:
                    page_counter += 1

        self.write_to_csv(apartments_data)

        driver.quit()
