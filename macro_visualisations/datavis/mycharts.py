import matplotlib as mpl
import matplotlib.pyplot as plt
import datavis.tsget as tg
import numpy as np
from ipywidgets import interactive
import ipywidgets as widgets
from IPython.display import display

def int_line(series, figsize=(6,4)):
    """Plots an interactive line chart for a TimeSeries object as created by
    tsget.TimeSeries
    """
    
    # Must be a better way of implementing this! Set facecolor so that chart displays 
    # on dark theme in JupyterLab
    mpl.rcParams['figure.facecolor'] = 'w'

    def line(start=0, end=1):
        """Function to call with interactive
        
        """
        start_loc = int(np.round(start * (len(series.timeseries)-1)))
        end_loc = int(np.round(end * (len(series.timeseries)-1)))

        sliced_data=series.timeseries.iloc[start_loc:end_loc]

        plt.figure(figsize=figsize)

        plt.title(series.name)
        plt.plot(sliced_data.index,sliced_data)
        plt.xticks(rotation=90)
        plt.grid(True)

        plt.plot()
    
    chart = interactive(line, start=(0, 1.0, 0.001), end=(0, 1.0, 0.001))
    display(chart)

def int_MAs(series, figsize=(6,4)):
    
    # Must be a better way of implementing this! Set facecolor so that chart displays 
    # on dark theme in JupyterLab
    mpl.rcParams['figure.facecolor'] = 'w'
    
    MAs = tg.windows(series)
    
    def moving_avg(rolling_mean = True, exp_mean = False, start=0, end=1):

         # The mask variables are boolean lists with True if column name has specified string
        # in, but all values are False if the "rolling_mean" or "exp_mean" variables are
        # set to False
        mask_rm = MAs.columns.str.contains('_MA', regex=False) * rolling_mean
        mask_em = MAs.columns.str.contains('_expMA', regex=False) * exp_mean
        mask = mask_rm + mask_em
        mask[0] = True

        start_loc = int(np.round(start * (len(MAs)-1)))
        end_loc = int(np.round(end * (len(MAs)-1)))

        sliced_data=MAs.loc[:,mask].iloc[start_loc:end_loc]

        plt.figure(figsize=figsize)

        plt.title(series.name)
        plt.plot(sliced_data.index,sliced_data)
        plt.xticks(rotation=90)
        plt.grid(True)

        plt.plot()
        
        print(" ")
        print(sliced_data.tail(1).T)
        print(" ")
           
    chart = interactive(moving_avg, rolling_mean=False, exp_mean=False,
                     start=(0.0, 1.0, 0.001), end=(0.0, 1.0, 0.001))
    display(chart)
    
    
    