from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from scrapers.MyHomeScraper import MyHomeScraper
from scrapers.LivoScraper import LivoScraper
from scrapers.SSHomeScraper import SSHomeScraper
from data_cleaning.DataCleaning import DataCleaning
from data_cleaning.ApartmentsDataFrame import ApartmentsDataFrame
from datastorage.csv.CSV import CSV
from data_analysis.RunEDA import RunEDA
from concurrent.futures import ThreadPoolExecutor



if __name__ == "__main__":
    """ Step 1: Scraping the data"""
    def run_myhome():
        MyHomeScraper().scraper(deal_types=[1,2])

    def run_livo():
        LivoScraper().scraper(deal_types=[1,2])

    def run_sshome():
        SSHomeScraper().scraper(deal_types=[1])

    with ThreadPoolExecutor(max_workers=3) as executor:
        for future in [executor.submit(run_myhome), executor.submit(run_sshome), executor.submit(run_livo)]:
            future.result()  # Ensures any exceptions are raised

    """ Step 2: Data cleaning and transformation """
    apartments_df = ApartmentsDataFrame().get_df()
    data_cleaning = DataCleaning(apartments_df)
    data_cleaning.normalize()
    data_cleaning.write_to_csv()

    """ Step 3: Save data in the datastorage """
    postgresql_database = PostgresDatabase()
    postgresql_database.database_insertion()

    csv = CSV()
    csv.deduplicate_and_write()

    """ Step 4: Data Analysis """
    run_eda = RunEDA()
    run_eda.run()
