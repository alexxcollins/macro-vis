from fredapi import Fred
import quandl as qd
import numpy as np
from datetime import datetime as dt
import pandas as pd
from pandas_datareader import data
qd.ApiConfig.api_key = "Pn4VQFgZqt6Uid7qWa_p"
# initialise the API key. Can pass key directly into Fred()
# or point to a file. I have saved
# api key into file below.
fred = Fred(api_key_file='/home/alex/alex/projects/datascienceprojects'
            '/apis/fredapikey.txt')


# create dictionary of quandl bundesbank codes
bb_code = {1: "BBK01_WT3400",
           2: "BBK01_WT3401",
           3: "BBK01_WT3402",
           4: "BBK01_WT3403",
           5: "BBK01_WT3404",
           7: "BBK01_WT3406",
           10: "BBK01_WT3409",
           15: "BBK01_WT3439",
           20: "BBK01_WT3449",
           30: "BBK01_WT3429"}

data_codes_fp = ('~/alex/projects/datascienceprojects/'
                 + 'macro_visualisations/ref_data/data_codes.csv')

data_codes = pd.read_csv(data_codes_fp, index_col=0)


class TimeSeries():
    # class of any time series from any data provider (hopefully!)

    def __init__(self, code='egeg5ycpy',
                 start=dt(2019, 1, 1), end=dt.today()):
        self.name = data_codes.at[code, 'name']
        self.provider_code = data_codes.at[code, 'provider_code']
        self.data_provider = data_codes.at[code, 'data_provider']
        self.currency = data_codes.at[code, 'currency']
        self.issuer = data_codes.at[code, 'issuer']
        self.asset_type = data_codes.at[code, 'asset_type']
        self.maturity = data_codes.at[code, 'maturity']
        self.maturity_unit = data_codes.at[code, 'maturity_unit']
        self.maturity_type = data_codes.at[code, 'maturity_type']
        self.unit = data_codes.at[code, 'unit']
        self.original_data_supplier = data_codes.at[code,
                                                    'original_data_supplier']
        self.start = start
        self.end = end
        self.timeseries = qd.get(
            self.provider_code,
            start_date=start,
            end_date=end)


class Bund():
    # German bund yields constant maturity

    def __init__(self, mat=5,
                 start=dt(2019, 1, 1), end=dt.today()):
        self.mat = mat
        self.start = start
        self.end = end
        code = 'BUNDESBANK/' + bb_code[mat]
        self.code = code
        self.timeseries = qd.get(
            code,
            start_date=start,
            end_date=end
        )


class Gilt():
    # Gilt bund yields constant maturity.
    # BOE data only available for 5, 10, 20y maturity


def ts_get(code, start, end, provider):
    # Get time series data from various providers
    # Returns a dataframe object
    if provider == 'quandl':
        ts = qd.get(
            code,
            start_date=start,
            end_date=end
        )
    elif provider == 'FRED':
        ts = pd.DataFrame(fred.get_series(series_id=code,
                                          observation_start=start,
                                          observation_end=end
                                          )
                          )
    return ts


def bund_curve(maturities=[1, 2, 3, 4, 5, 7, 10, 15, 20, 30],
               start=dt(2019, 1, 1),
               end=dt.today()):

    for i, y in enumerate(maturities):
        # i for list position, y for maturity (i.e. list entry)
        #     col_name = bund_objects[i]
        col_name = 'bund_' + str(y) + 'y'
        this_bund = Bund(y, start, end)
        # if at first stage of iteration, need to create the dataframe
        if i == 0:
            df = pd.DataFrame(this_bund.timeseries, columns=[col_name])
        df[col_name] = this_bund.timeseries

    return df
