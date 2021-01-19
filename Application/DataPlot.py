import os
import pandas
import glob
import matplotlib.pyplot as plt


class DataPlot:
    def __init__(self, path_to_data, export_path):
        self.width, self.height = 800, 500
        self.data = self.read_data_from_dir(path_to_data)
        self.export_path = export_path
        
    def read_data_from_dir(self, dir_path):
        dataframes = []
        for csv in  sorted(glob.glob(f"{dir_path}/*.csv")):
            dataframes.append(pandas.read_csv(csv, index_col=0))
        
        return dataframes

    def create_plot(self):
        # for df in self.data:
        #     plt.figure()
        #     df.plot(kind="bar")
            # print(df.plot.bar())
        pass

    def export_plot(self):
        dirs, file = os.path.split(self.export_path)
        os.makedirs(dirs, exist_ok=True)
        # write plot method

    def render_and_export_graph(self):
        self.create_plot()
        self.export_plot()
