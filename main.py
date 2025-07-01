from src.scrapers.MyHomeScraper import MyHomeScraper
from src.data_cleaning.DataCleaning import DataCleaning
from database.Database import Database



if __name__ == "__main__":
    """ Step 1: Scrape the data"""
    # myhome_scraper = MyHomeScraper()
    # myhome_scraper.main()

    """ Step 2: Data cleaning and transformation """
    path_to_cleaned_csv = "data_output/cleaned_apartments.csv"

    # data_cleaning = DataCleaning()
    # data_cleaning.main()
    # data_cleaning.write_to_csv(path_to_cleaned_csv)

    """ Step 3: Save data in the database """
    database = Database()
    database.setup_database()
