from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException



class SSHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://home.ss.ge/ka/udzravi-qoneba/"
        self.city_id_dict = {'თბილისი': 95, "ქუთაისი": 97, 'ბათუმი': 96}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 2
        self.raw_apartments_csv_path = 'data_output/sshome_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://home.ss.ge/ka/udzravi-qoneba/l/bina?cityIdList={id}&order=1&page={page}'

    def scraper(self):
        """ Main function to scrape the data from home.ss.ge website """
        driver = self.configure_chromedriver()
        apartments_data = []

        try:
            for city_name, city_id in self.city_id_dict.items():
                page_counter = 1

                while page_counter <= self.number_of_pages_to_scrape:
                    driver.get(self.get_url(city_id, page_counter))

                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")

                    listing_container = self.safe_find_element(driver, By.CLASS_NAME, "listing-container")
                    top_grid_lard = self.safe_find_element(listing_container, By.CLASS_NAME, "top-grid-lard")
                    child_divs = top_grid_lard.find_elements(By.TAG_NAME, "div")
                    grid = child_divs[0]

                    if not self.wait_for_links(grid, '', selector='a'):
                        print(f"{self.main_url} - Skipping Page: {page_counter} — links not loaded")
                        page_counter += 1
                        continue

                    a_tags = grid.find_elements(By.CSS_SELECTOR, 'a')  # finds all <a> tags

                    for a in a_tags:
                        try:
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

                            create_date = self.safe_find_element(a, By.CLASS_NAME, 'create-date')
                            upload_date = create_date.text if create_date else None

                            apartments_data.append({
                                'url': href,
                                'city': city_name,
                                'price': price,
                                'price_per_sqm': None,
                                'description': description,
                                'district_name': 'არ არის მოწოდებული',
                                'street_address': street_address,
                                'area_m2': area_m2,
                                'upload_date': upload_date
                            })

                        except StaleElementReferenceException:
                            print(f"{self.main_url} - Skipped page due to stale element error: "
                                  f"{city_name}, Page: {page_counter}")
                            break

                        except Exception as parse_err:
                            print(f"{self.main_url} - Error parsing apartment card: {parse_err}")
                            break

                    page_counter += 1

            self.write_to_csv(apartments_data)

        except Exception as e:
            print(f"{self.main_url} - Failed to load page or parse listings:", str(e))

        finally:
            driver.quit()
