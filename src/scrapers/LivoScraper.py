from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By


class LivoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.main_url = "https://livo.ge/"
        self.city_id_dict = {'თბილისი': 1, "ქუთაისი": 96, 'ბათუმი': 15}  # Cities with ids on this website
        self.number_of_pages_to_scrape = 1
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

                    apartments = self.wait_for_links(driver, 'udzravi-qoneba', selector='a.item-url')
                    if len(apartments) == 0:
                        print(f"{self.main_url} - Skipping Page: {page_counter} — links not loaded")
                        page_counter += 1
                        continue

                    for a in apartments:
                        try:
                            parent = a.find_element(By.XPATH, '..')  # Get parent of the <a> tag
                            siblings = parent.find_elements(By.XPATH, './div')

                            # Data is divided in two divs
                            div_0 = siblings[0]
                            div_1 = siblings[1]

                            price_el = self.safe_find_element(div_0, By.XPATH, './div/div/div/div[1]')
                            if price_el:
                                price_text = price_el.text.strip().replace(",", "")
                                if price_text.isdigit():
                                    price = price_text + " $"
                                else:
                                    continue
                            else:
                                continue

                            square_tag = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__square-tag')
                            price_per_sqm = square_tag.find_element(By.XPATH,
                                                                    '../..').text.strip() if square_tag else None

                            description_el = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__title')
                            description = description_el.text.strip() if description_el else None

                            address_el = self.safe_find_element(div_0, By.CLASS_NAME, 'statement__address')
                            street_address = address_el.get_attribute("title").strip() if address_el else None

                            info_class = 'card-additional-info__item'

                            try:
                                area_m2 = self.safe_find_element(div_1, By.XPATH,
                                f'.//div[contains(@class, {info_class})][1]').text.split()[1].strip()
                            except:
                                area_m2 = None

                            try:
                                bedrooms = self.safe_find_element(div_1, By.XPATH,
                            f'.//div[contains(@class, {info_class}) and contains(text(), "საძ.")]').text.strip()
                            except:
                                bedrooms = None

                            try:
                                floor = self.safe_find_element(div_1, By.XPATH,
                            f'.//div[contains(@class, {info_class}) and contains(text(), "სართ.")]').text.strip()
                            except:
                                floor = None

                            try:
                                spans = div_1.find_elements(By.TAG_NAME, 'span')
                                upload_date = spans[1].text if len(spans) > 1 else None
                            except:
                                upload_date = None

                            apartments_data.append({
                                'url': a.get_attribute('href'),
                                'city': city_name,
                                'price': price,
                                'price_per_sqm': price_per_sqm,
                                'description': description,
                                'district_name': 'არ არის მოწოდებული',
                                'street_address': street_address,
                                'bedrooms': bedrooms,
                                'floor': floor,
                                'area_m2': area_m2,
                                'upload_date': upload_date
                            })

                        except Exception as parse_err:
                            print(f"{self.main_url} - Error parsing apartment card: {parse_err}")
                            continue

                    page_counter += 1

            self.write_to_csv(apartments_data)

        except Exception as e:
            print(f"{self.main_url} -Failed to load page or parse listings:", str(e))

        finally:
            driver.quit()
