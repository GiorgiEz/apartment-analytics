from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from pathlib import Path


class DataAnalysis(ABC):
    def __init__(self, df, output_dir):
        self.df = df
        self.output_dir = Path(output_dir)

    @abstractmethod
    def generate(self):
        """ Every child class should implement this method. """
        return NotImplementedError("Needs to be implemented by child classes")

    def save_fig(self, fig, filename):
        fig.savefig(self.output_dir / filename, bbox_inches="tight")
        plt.close(fig)
