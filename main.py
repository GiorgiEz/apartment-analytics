from src.scrapers.MyHomeScraper import MyHomeScraper
from src.data_cleaning.DataCleaning import DataCleaning
from database.Database import Database
from src.data_analysis.DataAnalysis import DataAnalysis



if __name__ == "__main__":
    """ Step 1: Scrape the data"""
    # myhome_scraper = MyHomeScraper()
    # myhome_scraper.scraper()

    """ Step 2: Data cleaning and transformation """

    # data_cleaning = DataCleaning()
    # data_cleaning.main()
    # data_cleaning.write_to_csv()

    """ Step 3: Save data in the database """
    # database = Database()
    # database.setup_database()

    """ Step 4: Data Analysis """
    data_analysis = DataAnalysis()
    data_analysis.main()
