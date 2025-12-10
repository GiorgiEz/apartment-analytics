from scrape_clean_analyze.scrapers.BaseScraper import BaseScraper
from scrape_clean_analyze.scrapers.MyHomeScraper import MyHomeScraper
from scrape_clean_analyze.scrapers.LivoScraper import LivoScraper
from scrape_clean_analyze.scrapers.SSHomeScraper import SSHomeScraper
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning
from database.Database import Database
from scrape_clean_analyze.data_analysis.RunEDA import RunEDA
from concurrent.futures import ThreadPoolExecutor



if __name__ == "__main__":
    """ Step 1: Scraping the data"""
    def run_myhome():
        MyHomeScraper().scraper()

    def run_livo():
        LivoScraper().scraper()

    def run_sshome():
        SSHomeScraper().scraper()

    with ThreadPoolExecutor(max_workers=2) as executor:
        for future in [executor.submit(run_myhome), executor.submit(run_sshome)]:
            future.result()  # Ensures any exceptions are raised

    """ Step 2: Data cleaning and transformation """
    data_cleaning = DataCleaning()
    data_cleaning.main()
    data_cleaning.write_to_csv()

    """ Step 3: Save data in the database """
    database = Database()
    database.setup_database()

    """ Step 4: Data Analysis """
    run_eda = RunEDA()
    run_eda.main()
