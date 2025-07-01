from .BaseScraper import BaseScraper
from selenium.webdriver.common.by import By
import time



class MyHomeScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        # Cities with their ids on myhome.ge website, to use while entering the URL
        self.city_id_dict = {"ქუთაისი": 96, 'თბილისი': 1, 'ბათუმი': 15}
        self.number_of_pages_to_scrape = 10

    def get_url(self, id, page):
        """ URL for apartment listings (not including houses, hotels or other real estate types)"""
        # MAIN_URL = "https://www.myhome.ge/"
        return f'https://www.myhome.ge/s/?currency_id=1&CardView=1&real_estate_types=1&cities={id}&page={page}'
    
    def is_no_results_message_present(self, driver):
        """Check if any <p> tag contains the text 'განცხადებები ვერ მოიძებნა'."""
        p_tags = driver.find_elements(By.TAG_NAME, "p")

        for p in p_tags:
            if "განცხადებები ვერ მოიძებნა" in p.text.strip():
                return True
        return False
    
    def scraper(self):
        driver = self.configure_chromedriver()
        apartments_data = []

        try:
            for city_name, city_id in self.city_id_dict.items():
                page_counter = 1
                print("City: ", city_name)

                while page_counter <= self.number_of_pages_to_scrape:
                    driver.get(self.get_url(city_id, page_counter))
                    time.sleep(1)
                    
                    if self.is_no_results_message_present(driver):
                        print("No listings found on this page. Stopping pagination.")
                        break

                    print("Page: ", page_counter)

                    all_links = driver.find_elements(By.TAG_NAME, 'a')  # finds all <a> tags

                    for a in all_links:
                        href = a.get_attribute('href')  # We only want links that are links of uploaded apartments
                        if not href or not ('https://www.myhome.ge/pr' in str(href)):
                            continue
                        
                        try: 
                            # Each <a> contains 2 direct divs. 2nd div is where the main data is stored
                            data_div = a.find_elements(By.CSS_SELECTOR, ':scope > div')[1]

                            # 2nd div contains 5 divs, each div containing specific data
                            data_div_info = data_div.find_elements(By.CSS_SELECTOR, ':scope > div')

                            price = None
                            price_per_sqm = None
                            description = None
                            street_number = None
                            area_m2 = None
                            street_name = None
                            upload_date = None

                            if len(data_div_info) >= 5:
                                # The First div of data_div_info contains data about the price and price_per_sqm
                                spans_0 = data_div_info[0].find_elements(By.TAG_NAME, "span")
                                price = spans_0 [0].text if len(spans_0 ) > 0 else None
                                price_per_sqm = spans_0 [3].text if len(spans_0 ) == 4 else None

                                # The Second div of data_div_info contains data about the description
                                description_h2 = data_div_info[1].find_element(By.TAG_NAME, "h2")
                                description = description_h2.text if description_h2 else None

                                # The Third div of data_div_info contains data about the street number
                                street_number_h3 = data_div_info[2].find_element(By.TAG_NAME, "h3")
                                street_number = street_number_h3.text if street_number_h3 else None

                                # The Fourth div of data_div_info contains data about the area_m2
                                spans_3 = data_div_info[3].find_elements(By.TAG_NAME, "span")
                                if "მ²" in spans_3[-1].text:
                                    area_m2 = (spans_3[-2].text + spans_3[-1].text).strip()

                                # The Fifth div of the data_div_info contains data about the street_name and upload_date
                                spans_4 = data_div_info[4].find_elements(By.TAG_NAME, "span")
                                street_name = spans_4[0].text if len(spans_4) > 0 else None
                                upload_date = spans_4[1].text if len(spans_4) > 1 else None

                            apartments_data.append({
                                'url': href,
                                'city': city_name,
                                'price': price,
                                'price_per_sqm': price_per_sqm,
                                'description': description,
                                'street_name': street_name,
                                'street_number': street_number,
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

    def main(self):
        self.scraper()
