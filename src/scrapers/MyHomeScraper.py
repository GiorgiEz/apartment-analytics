from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
import time



class MyHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Cities with their ids on myhome.ge website, to use while entering the URL
        # self.city_id_dict = {"ქუთაისი": 96, 'თბილისი': 1, 'ბათუმი': 15}
        self.city_id_dict = {"ქუთაისი": 96}

    def get_url(self, id):
        """ URL for apartment listings (no including houses, hotels or other real estate types)"""
        # MAIN_URL = "https://www.myhome.ge/"
        return f'https://www.myhome.ge/s/?currency_id=1&CardView=1&real_estate_types=1&cities={id}&page=1'

    def scraper(self):
        driver = self.configure_chromedriver()

        try:
            for city_name, id in self.city_id_dict.items():
                driver.get(self.get_url(id))

                time.sleep(2)
                all_links = driver.find_elements(By.TAG_NAME, 'a')  # finds all <a> tags

                for a in all_links:
                    href = a.get_attribute('href')  # We only want links that are links of uploaded apartments
                    if href and 'https://www.myhome.ge/pr' in str(href):
                        url = href
                        city = city_name

                        # Each <a> contains 2 direct divs, the 2nd div is where the main data is stored
                        data_div = a.find_elements(By.CSS_SELECTOR, ':scope > div')[1]

                        # 2nd div contains 5 divs, each div containing specific data
                        data_div_info = data_div.find_elements(By.CSS_SELECTOR, ':scope > div')

                        data_div_info_0_spans = data_div_info[0].find_elements(By.TAG_NAME, "span")
                        price = data_div_info_0_spans[0].text if len(data_div_info_0_spans) > 0 else None
                        price_per_area_m2 = data_div_info_0_spans[3].text if len(data_div_info_0_spans) == 4 else None

                        description_h2 = data_div_info[1].find_element(By.TAG_NAME, "h2")
                        description = description_h2.text if description_h2 else None

                        street_number = data_div_info[2].find_element(By.TAG_NAME, "h3").text

                        area_m2 = None
                        data_div_info_3_spans = data_div_info[3].find_elements(By.TAG_NAME, "span")
                        if "მ²" in data_div_info_3_spans[-1].text:
                            area_m2 = (data_div_info_3_spans[-2].text + data_div_info_3_spans[-1].text).strip()

                        data_div_info_4_spans = data_div_info[4].find_elements(By.TAG_NAME, "span")
                        street_name = data_div_info_4_spans[0].text if len(data_div_info_4_spans) > 0 else None
                        date_uploaded = data_div_info_4_spans[1].text if len(data_div_info_4_spans) > 1 else None

                        print(url, city, price, price_per_area_m2, description, street_name,
                              street_number, area_m2, date_uploaded)


        except Exception as e:
            print("Failed to load page or parse listings:", str(e))

        finally:
            driver.quit()

    def main(self):
        self.scraper()
