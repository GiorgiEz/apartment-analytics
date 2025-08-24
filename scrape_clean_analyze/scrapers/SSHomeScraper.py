import pandas as pd
from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException



class SSHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://home.ss.ge/ka/udzravi-qoneba/"
        self.city_id_dict = {'თბილისი': 95, "ქუთაისი": 97, 'ბათუმი': 96}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 5
        self.raw_apartments_csv_path = '../data_output/sshome_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://home.ss.ge/ka/udzravi-qoneba/l/bina?cityIdList={id}&order=1&page={page}'

    def scraper(self):
        """ Main function to scrape the data from home.ss.ge website """
        driver = self.configure_chromedriver()
        apartments_data = []

        for city_name, city_id in self.city_id_dict.items():
            page_counter = 1

            while page_counter <= self.number_of_pages_to_scrape:
                try:
                    driver.get(self.get_url(city_id, page_counter))

                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")

                    try:  # Finding the main div grid where the data about apartments is located
                        listing_container = self.safe_find_element(driver, By.CLASS_NAME, "listing-container")
                        top_grid_lard = self.safe_find_element(listing_container, By.CLASS_NAME, "top-grid-lard")
                        child_divs = top_grid_lard.find_elements(By.TAG_NAME, "div")
                        grid = child_divs[0]
                    except Exception as e:
                        print(f"{self.main_url} - Error finding grid at Page: {page_counter}, skipping page: {e}")
                        page_counter += 1
                        continue

                    a_tags = self.wait_for_links(grid, '', selector='a')
                    if len(a_tags) == 0:  # If there are not a_tags found then we skip the page
                        page_counter += 1
                        continue

                    for a in a_tags:
                        href = str(a.get_attribute('href'))
                        if not href or self.main_url not in href:
                            continue

                        price_span = self.safe_find_element(a, By.CLASS_NAME, 'listing-detailed-item-price')
                        if not price_span or ("$" not in price_span.text and "₾" not in price_span.text):
                            continue
                        price = price_span.text

                        desc_h2 = self.safe_find_element(a, By.CLASS_NAME, 'listing-detailed-item-title')
                        description = desc_h2.text if desc_h2 else None

                        addr_span = self.safe_find_element(a, By.CLASS_NAME, 'listing-detailed-item-address')
                        street_address = addr_span.text if addr_span else None

                        area_span = self.safe_find_element(a, By.CLASS_NAME, "icon-crop_free")
                        area_span_parent = area_span.find_element(By.XPATH, './..') if area_span else None
                        area_m2 = area_span_parent.text if area_span_parent else None

                        bedroom_span = self.safe_find_element(a, By.CLASS_NAME, "icon-bed")
                        bedroom_parent = bedroom_span.find_element(By.XPATH, './..') if bedroom_span else None
                        bedrooms = bedroom_parent.text if bedroom_parent else None

                        floor_span = self.safe_find_element(a, By.CLASS_NAME, "icon-stairs")
                        floor_span_parent = floor_span.find_element(By.XPATH, './..') if floor_span else None
                        floor = floor_span_parent.text if floor_span_parent else None

                        create_date = self.safe_find_element(a, By.CLASS_NAME, 'create-date')
                        upload_date = create_date.text if create_date else None

                        apartments_data.append({
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
