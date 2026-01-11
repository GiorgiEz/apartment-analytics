from datastorage.postgresql.PostgresDatabase import PostgresDatabase


class DataAnalysis:
    def __init__(self):
        db = PostgresDatabase()
        self.df = db.get_all_apartments()

        self.image_path = '../frontend/src/charts/'

    def run(self, *args):
        """ Every child class should implement this method. """
        return NotImplementedError("Needs to be implemented by child classes")
