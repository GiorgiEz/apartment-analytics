import pandas as pd
from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from ..utils.helpers import geo_months


class LivoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://livo.ge/"
        self.city_id_dict = {'თბილისი': 1, "ქუთაისი": 96, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 10
        self.raw_apartments_csv_path = '../data_output/livo_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types) """
        return f'https://livo.ge/s/gancxadebebis-sia?real_estate_types=1&cities={id}&page={page}'

    def scraper(self):
        """ Main function to scrape the data from livo.ge website """
        driver = self.configure_driver()
        apartments_data = []

        for city_name, city_id in self.city_id_dict.items():
            page_counter = 1

            while page_counter <= self.number_of_pages_to_scrape:
                try:
                    driver.get(self.get_url(city_id, page_counter))
                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")

                    apartments = self.wait_for_links(driver, 'udzravi-qoneba', selector='a.item-url')
                    if len(apartments) == 0:
                        print(f"{self.main_url} - Skipping Page: {page_counter} — links not loaded")
                        page_counter += 1
                        continue

                    for a in apartments:
                        parent = a.find_element(By.XPATH, '..')  # Get parent of the <a> tag
                        divs = parent.find_elements(By.XPATH, './div')

                        # 1. div for price, price_per_sqm, description, street_address
                        div_0 = divs[0].find_elements(By.XPATH, './div')[1].text.splitlines()

                        price = div_0[0] + '$' if len(div_0) > 0 else pd.NA
                        price_per_sqm = div_0[3] if len(div_0) > 3 and 'მ2' in div_0[3] else pd.NA
                        description = div_0[4] if len(div_0) > 4 else pd.NA
                        street_address = div_0[5] if len(div_0) > 5 else pd.NA

                        # 2. div for area, bedrooms, floor and upload date
                        area_m2, bedrooms, floor, upload_date = pd.NA, pd.NA, pd.NA, pd.NA
                        div_1 = divs[1].text.splitlines()
                        for info in div_1:
                            if 'მ2' in info:
                                area_m2 = info
                            elif 'საძ' in info:
                                bedrooms = info
                            elif 'სართ' in info:
                                floor = info
                            elif any(m in info for m in geo_months.keys()):
                                upload_date = info

                        if pd.isna(price) or pd.isna(street_address) or pd.isna(upload_date):
                            continue

                        apartments_data.append({
                            'url': a.get_attribute('href'),
                            'city': city_name,
                            'price': price,
                            'price_per_sqm': price_per_sqm,
                            'description': description,
                            'district_name': pd.NA,
                            'street_address': street_address,
                            'bedrooms': bedrooms,
                            'floor': floor,
                            'area_m2': area_m2,
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
