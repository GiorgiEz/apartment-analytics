from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import os
from pathlib import Path
from config import paths


class DataAnalysis(ABC):
    def __init__(self):
        self.output_dir = Path(paths.BACKEND_CHARTS_DIR)
        self.CITY_MAP = {"თბილისი": "Tbilisi", "ბათუმი": "Batumi", "ქუთაისი": "Kutaisi"}
        self.cities = ["ქუთაისი", "ბათუმი", "თბილისი"]
        # light blue, light orange, light green
        self.city_colors = {
            "Tbilisi": "#AEC7E8", "Batumi": "#FFBB78", "Kutaisi": "#98DF8A",
            "თბილისი": "#AEC7E8", "ბათუმი": "#FFBB78", "ქუთაისი": "#98DF8A"
        }
        self.transaction_colors = {"Sale": "#6FA8DC", "Rent": "#82C596"}
        self.figsize = (14, 10)
        self.styles = {
            "title": {"fontsize": 16, "fontweight": "bold", "pad": 20},
            "suptitle": {"fontsize": 16, "fontweight": "bold", "y": 1.03},
            "bar_label": {"ha": "center", "va": "bottom", "fontsize": 14, "fontweight": "bold"},
            "axis_title": {"fontsize": 12},
            "axis_ticks": {"labelsize": 12},
            "grid": {"linestyle": "--", "alpha": 0.5},

            "pie_textprops": {"fontsize": 14, "fontweight": "bold", "color": "black"},
        }

    def style_axes(self, ax=None, fig=None, max_height=None, y_numeric=True):
        """ Remove top and right lines from bar charts and enable grid and add number formatting """
        if ax:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.grid(axis="y", **self.styles["grid"])
            if y_numeric:
                ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))

            ax.tick_params(axis="x", **self.styles["axis_ticks"])
            ax.tick_params(axis="y", **self.styles["axis_ticks"])

        if max_height:
            ax.set_ylim(0, max_height * 1.1)

        if fig:
            fig.tight_layout()

    def bar_label_offset(self, max_height):
        """ Offset between the bar and the label """
        return max_height * 0.01

    def lighten_color(self, color, amount=0.3):
        """ Lightens the given color. amount: 0 → original, 1 → white """
        c = mcolors.to_rgb(color)
        return tuple(1 - (1 - x) * (1 - amount) for x in c)

    @abstractmethod
    def generate(self):
        """ Every child class should implement this method. """
        return NotImplementedError("Needs to be implemented by child classes")

    def save_fig(self, fig, filename):
        """ Saves plots and charts as png files. """
        os.makedirs(self.output_dir, exist_ok=True)  # Create directory if not exists
        fig.savefig(self.output_dir / filename, bbox_inches="tight")
        plt.close(fig)
