import sqlite3
import pandas as pd



class DataAnalysis:
    def __init__(self):
        conn = sqlite3.connect('../database/apartments.db')
        self.df = pd.read_sql_query("SELECT * FROM apartments", conn)  # Gets all the data from the apartments.db
        conn.close()

        self.image_path = '../frontend/src/charts/'

    def run(self, *args):
        """ Every child class should implement this method. """
        return NotImplementedError("Needs to be implemented by child classes")
