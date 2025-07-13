import pandas as pd



class ApartmentsDataFrame:
    """Singleton class to manage a single DataFrame of all apartments """

    _instance = None

    def __new__(cls, livo_apartments_csv="data_output/livo_apartments.csv",
                myhome_apartments_csv="data_output/myhome_apartments.csv",
                sshome_apartments_csv="data_output/sshome_apartments.csv",):
        """Ensures only one instance is created."""
        if cls._instance is None:
            cls._instance = super(ApartmentsDataFrame, cls).__new__(cls)
            cls._instance.init_data(livo_apartments_csv, myhome_apartments_csv, sshome_apartments_csv)
        return cls._instance

    def init_data(self, livo_csv, myhome_csv, sshome_csv):
        """Loads data from CSV files and merges them into a single DataFrame."""
        ss_home_df = pd.read_csv(sshome_csv)
        my_home_df = pd.read_csv(myhome_csv)
        livo_df = pd.read_csv(livo_csv)
        self.df = pd.concat([livo_df, my_home_df, ss_home_df], ignore_index=True)
        print(f"DataFrame loaded with {len(self.df)} records.")

    def get_df(self):
        """Returns the DataFrame instance."""
        return self.df
