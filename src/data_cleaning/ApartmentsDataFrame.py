import pandas as pd



class ApartmentsDataFrame:
    """Singleton class to manage a single DataFrame of all apartments """

    _instance = None

    def __new__(cls, apartments_csv="data_output/raw_apartments.csv"):
        """Ensures only one instance is created."""
        if cls._instance is None:
            cls._instance = super(ApartmentsDataFrame, cls).__new__(cls)
            cls._instance.init_data(apartments_csv)
        return cls._instance

    def init_data(self, apartments_csv):
        """Loads data from CSV files and merges them into a single DataFrame."""
        self.apartments_df = pd.read_csv(apartments_csv)
        print(f"✅ DataFrame loaded with {len(self.apartments_df)} records.")

    def get_df(self):
        """Returns the DataFrame instance."""
        return self.apartments_df
