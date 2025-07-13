from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException



class MyHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://www.myhome.ge/"
        self.city_id_dict = {'თბილისი': 1, "ქუთაისი": 96, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 2
        self.raw_apartments_csv_path = 'data_output/myhome_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://www.myhome.ge/s/?CardView=1&real_estate_types=1&cities={id}&page={page}'

    def scraper(self):
        """ Main function to scrape the data from myhome.ge website """
        driver = self.configure_chromedriver()
        apartments_data = []

        try:
            for city_name, city_id in self.city_id_dict.items():
                page_counter = 1

                while page_counter <= self.number_of_pages_to_scrape:
                    driver.get(self.get_url(city_id, page_counter))

                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")
                    if not self.wait_for_links(driver, 'pr', timeout=10):
                        print(f"Skipping Page: {page_counter} — links not loaded")
                        page_counter += 1
                        continue

                    a_tags = driver.find_elements(By.TAG_NAME, 'a')  # finds all <a> tags
                    apartments = [a for a in a_tags if self.main_url + 'pr' in str(a.get_attribute('href'))]

                    for a in apartments:
                        try:
                            try:
                                # Wait up to 5 seconds to return 5 div elements
                                WebDriverWait(a, 5).until(
                                    lambda driver: len(a.find_elements(By.XPATH, "./div[2]/div")) == 5
                                )
                                data_div_info = a.find_elements(By.XPATH, "./div[2]/div")

                            except TimeoutException:
                                print(f"{self.main_url} - Skipping this listing — expected 5 data_div_info elements.")

                                continue

                            # The First div of data_div_info contains data about the price and price_per_sqm
                            spans_0 = data_div_info[0].find_elements(By.TAG_NAME, "span")
                            price = spans_0[0].text if len(spans_0) > 0 else None
                            price_per_sqm = spans_0[3].text if len(spans_0) > 3 else None

                            # The Second div of data_div_info contains data about the description
                            description_h2 = data_div_info[1].find_element(By.TAG_NAME, "h2")
                            description = description_h2.text if description_h2 else None

                            # The Third div of data_div_info contains data about the street address
                            street_address_h3 = data_div_info[2].find_element(By.TAG_NAME, "h3")
                            street_address = street_address_h3.text if street_address_h3 else None

                            # The Fourth div of data_div_info contains data about the area_m2
                            spans_3 = data_div_info[3].find_elements(By.TAG_NAME, "span")
                            area_m2 = (spans_3[-2].text+spans_3[-1].text).strip() if "მ²" in spans_3[-1].text else None

                            # The 5th div of the data_div_info contains data about the district_name and upload_date
                            spans_4 = data_div_info[4].find_elements(By.TAG_NAME, "span")
                            district_name = spans_4[0].text if len(spans_4) > 0 else None
                            upload_date = spans_4[1].text if len(spans_4) > 1 else None

                            apartments_data.append({
                                'url': a.get_attribute('href'),
                                'city': city_name,
                                'price': price,
                                'price_per_sqm': price_per_sqm,
                                'description': description,
                                'district_name': district_name,
                                'street_address': street_address,
                                'area_m2': area_m2,
                                'upload_date': upload_date
                            })

                        except Exception as parse_err:
                            print(f"{self.main_url} - Error parsing apartment card: {parse_err}")
                            continue

                    page_counter += 1

            self.write_to_csv(apartments_data)

        except Exception as e:
            print(f"{self.main_url} - Failed to load page or parse listings:", str(e))

        finally:
            driver.quit()
