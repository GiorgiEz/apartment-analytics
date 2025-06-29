from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# URL for apartment listings
MAIN_URL = "https://www.myhome.com/"
URL = 'https://www.myhome.ge/s/bina/?currency_id=1&CardView=1&real_estate_types=1&page=1'


def scraper():
    # Configure Chrome
    options = Options()
    options.add_argument('--start-maximized')  # optional
    # options.add_argument('--headless')  # uncomment for headless mode
    options.add_argument('--disable-blink-features=AutomationControlled')  # avoid detection
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--blink-settings=imagesEnabled=false')

    # Initialize driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print(f"🌍 Opening: {URL}")
        driver.get(URL)

        # 1. Wait for the grid to appear
        wait = WebDriverWait(driver, 20)
        grid = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div[1]/div[4]/div/div[3]/div/div[2]')
        ))

        # 2. Wait until at least one <a> tag is present inside the grid
        wait.until(lambda d: len(grid.find_elements(By.TAG_NAME, 'a')) > 0)

        # 3. Then collect all <a> elements
        apartment_links = grid.find_elements(By.TAG_NAME, 'a')
        print(f"✅ Found {len(apartment_links)} apartment listings.")

    except Exception as e:
        print("❌ Failed to load page or parse listings:", str(e))

    finally:
        driver.quit()



if __name__ == "__main__":
    scraper()
