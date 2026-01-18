import pandas as pd

from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from scrape_clean_analyze.scrapers.MyHomeScraper import MyHomeScraper
from scrape_clean_analyze.scrapers.LivoScraper import LivoScraper
from scrape_clean_analyze.scrapers.SSHomeScraper import SSHomeScraper
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning
from data_cleaning.ApartmentsDataFrame import ApartmentsDataFrame
from datastorage.csv.CSV import CSV
from scrape_clean_analyze.data_analysis.RunEDA import RunEDA
from concurrent.futures import ThreadPoolExecutor
from config import paths

from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    """ Step 1: Scraping the data"""
    def run_myhome():
        MyHomeScraper().scraper()

    def run_livo():
        LivoScraper().scraper()

    def run_sshome():
        SSHomeScraper().scraper()

    # with ThreadPoolExecutor(max_workers=3) as executor:
    #     for future in [executor.submit(run_myhome), executor.submit(run_sshome), executor.submit(run_livo)]:
    #         future.result()  # Ensures any exceptions are raised
    #
    # """ Step 2: Data cleaning and transformation """
    # apartments_df = ApartmentsDataFrame().get_df()
    # data_cleaning = DataCleaning(apartments_df)
    # data_cleaning.normalize()
    # data_cleaning.write_to_csv()
    #
    # """ Step 3: Save data in the datastorage """
    # postgresql_database = PostgresDatabase()
    # postgresql_database.database_insertion()
    #
    # csv = CSV()
    # csv.deduplicate_and_write()
    #
    # """ Step 4: Data Analysis """
    # run_eda = RunEDA()
    # run_eda.main()
