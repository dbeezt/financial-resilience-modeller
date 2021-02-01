import os
import pandas
import glob
import matplotlib.pyplot as plt


class DataPlot:
    def __init__(self, path_to_data, export_path):
        self.width, self.height = 800, 500
        self.dataframes = self.read_data_from_dir(path_to_data)
        self.export_path = export_path
        self.init_plot_output_dir()


    def init_plot_output_dir(self):
        dirs, file = os.path.split(self.export_path)
        os.makedirs(dirs, exist_ok=True)
        
    def read_data_from_dir(self, dir_path):
        dataframes = []
        for csv in sorted(glob.glob(f"{dir_path}/*.csv")):
            dataframes.append(pandas.read_csv(csv, index_col=0))
        return dataframes

    def mean_fin_impact(self):
        x = range(0, len(self.dataframes))
        y = [df['current_asset_value'].mean() for df in self.dataframes]
        plt.plot(x, y, label = 'Mean Asset Value')
        plt.xlabel('Time')
        plt.ylabel('Financial Impact')
        plt.legend()
        plt.title('Decrease of Mean Asset Value over Time')
        plt.gcf().autofmt_xdate()
        plt.savefig(f"{self.export_path}/mean_fin_impact.png")
