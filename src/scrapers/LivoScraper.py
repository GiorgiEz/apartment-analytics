from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class LivoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://livo.ge/"
        self.city_id_dict = {"ქუთაისი": 96, 'თბილისი': 1, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 2
        self.raw_apartments_csv_path = 'data_output/livo_apartments.csv'

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        return f'https://livo.ge/s/gancxadebebis-sia?real_estate_types=1&cities={id}&page={page}'

    def scraper(self):
        """ Main function to scrape the data from livo.ge website """
        driver = self.configure_chromedriver()
        apartments_data = []

        try:
            for city_name, city_id in self.city_id_dict.items():
                page_counter = 1

                while page_counter <= self.number_of_pages_to_scrape:
                    driver.get(self.get_url(city_id, page_counter))

                    print(f"{self.main_url} - City: {city_name}, Page: {page_counter}")

                    # Wait until at least 10 matching <a> tags are found
                    WebDriverWait(driver, 2).until(
                        lambda d: len([
                            a for a in d.find_elements(By.CSS_SELECTOR, 'a.item-url')
                            if self.main_url + 'udzravi-qoneba' in str(a.get_attribute('href'))
                        ]) >= 10
                    )

                    a_tags = driver.find_elements(By.CSS_SELECTOR, 'a.item-url')  # finds all <a> tags
                    apartments = [a for a in a_tags if
                                  (self.main_url + 'udzravi-qoneba' in str(a.get_attribute('href')))]

                    for a in apartments:
                        try:
                            parent = a.find_element(By.XPATH, '..')  # Get parent of the <a> tag
                            siblings = parent.find_elements(By.XPATH, './div')

                            # Data is divided in two divs
                            div_0 = siblings[0]
                            div_1 = siblings[1]

                            price_el = self.safe_find_element(div_0, By.XPATH, './div/div/div/div[1]')
                            price = price_el.text.strip() if price_el else None

                            square_tag = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__square-tag')
                            price_per_sqm = square_tag.find_element(By.XPATH,
                                                                    '../..').text.strip() if square_tag else None

                            description_el = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__title')
                            description = description_el.text.strip() if description_el else None

                            address_el = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__address')
                            street_address = address_el.get_attribute("title").strip() if address_el else None

                            try:
                                area_m2 = div_1.find_element(By.XPATH,
                                    ".//div[contains(@class, 'card-additional-info__item')][1]").text.split()[1].strip()
                            except:
                                area_m2 = None

                            try:
                                upload_date = div_1.find_element(By.XPATH, ".//span[2]").text.strip()
                            except:
                                upload_date = None

                            apartments_data.append({
                                'url': a.get_attribute('href'),
                                'city': city_name,
                                'price': price,
                                'price_per_sqm': price_per_sqm,
                                'description': description,
                                'district_name': None,
                                'street_address': street_address,
                                'area_m2': area_m2,
                                'upload_date': upload_date
                            })

                        except Exception as parse_err:
                            print(f"Error parsing apartment card: {parse_err}")
                            continue

                    page_counter += 1

            self.write_to_csv(apartments_data)

        except Exception as e:
            print("Failed to load page or parse listings:", str(e))

        finally:
            driver.quit()
