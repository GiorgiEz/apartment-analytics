from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import os
from pathlib import Path
from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from config import paths


class DataAnalysis(ABC):
    def __init__(self):
        self.df = PostgresDatabase().get_all_apartments()
        self.output_dir = Path(paths.BACKEND_CHARTS_DIR)
        # light blue, light orange, light green
        self.city_colors = {"თბილისი": "#AEC7E8", "ბათუმი": "#FFBB78", "ქუთაისი": "#98DF8A"}
        self.figsize = (12, 8)

    @abstractmethod
    def generate(self):
        """ Every child class should implement this method. """
        return NotImplementedError("Needs to be implemented by child classes")

    def save_fig(self, fig, filename):
        """ Saves plots and charts as png files. """
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory if not exists
        fig.savefig(self.output_dir / filename, bbox_inches="tight")
        plt.close(fig)
