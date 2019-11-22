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

# a library of instrument vendor codes and other metadata is in the
# file below
fp = ('~/alex/projects/datascienceprojects/'
      + 'macro_visualisations/ref_data/')
data_codes = pd.read_csv(fp+'data_codes.csv', index_col=0)
issuers = pd.read_csv(fp+'issuers.csv', index_col=0)
ma_params = pd.read_csv(fp+'ma_params.csv')

class TimeSeries():
    """
    class to create time series objects from any data provider (hopefully!)
    """

    def __init__(self, code='egeg5ycpy',
                 start=dt(2019, 1, 1), end=dt.today()):
        self.name = data_codes.at[code, 'name']
        self.provider_code = data_codes.at[code, 'provider_code']
        self.data_provider = data_codes.at[code, 'data_provider']
        self.currency = data_codes.at[code, 'currency']
        self.currency_2 = data_codes.at[code, 'currency_2']
        self.issuer = data_codes.at[code, 'issuer']
        self.asset_type = data_codes.at[code, 'asset_type']
        self.maturity = data_codes.at[code, 'maturity']
        self.maturity_unit = data_codes.at[code, 'maturity_unit']
        self.maturity_type = data_codes.at[code, 'maturity_type']
        self.unit = data_codes.at[code, 'unit']
        self.original_data_supplier = data_codes.at[code, 'original_data_supplier']
        self.start = start
        self.end = end
        if self.original_data_supplier == 'fred':
            self.metadata = fred.search(self.provider_code)            
        self.timeseries = ts_get(
            code=self.provider_code,
            start=start,
            end=end,
            provider=self.data_provider
            )

class Data_Releases():
    """ Creates dataframe with dates for data as index and 
    2-level column name index. Columns are number of releases for that data point,
    and release date, release vale and release number for that release.
    The release number is for clarity - user may specify "second last" release, but
    it may be helpful to see that it's the fifth release, for example.
    
    Currently work in progress and copied from Jupyter Notebook - not yet finised.
    
    """
    def __init__(self, code, start=dt(1980,1,1), end=dt.today(), revisions=[0], revs_from_last=[0]):
        
        self.name = data_codes.at[code, 'name']
        self.provider_code = data_codes.at[code, 'provider_code']
        self.data_provider = data_codes.at[code, 'data_provider']
        self.currency = data_codes.at[code, 'currency']
        self.asset_type = data_codes.at[code, 'asset_type']
        self.original_data_supplier = data_codes.at[code,
                                                    'original_data_supplier']
        self.start = start
        self.end = end
        self.revisions = revisions
        self.revisions_from_end = revs_from_last
        if self.original_data_supplier == 'fred':
            self.metadata = fred.search(self.provider_code)            
        self.timeseries = ts_releases_get(code=self.provider_code,
                                          start=self.start,
                                          end=self.end,
                                          revisions=self.revisions, 
                                          revs_from_last=self.revisions_from_end,
                                          data_supplier=self.data_provider,
                                         )
        
def windows(data_obj, window_params = ma_params):

    """Returns DataFrame of moving averages for input series

    Inputs:
        window_params, DataFrame. DataFrame with integer index, columns are
        'window_length', 'min_periods', 'half_life' which are the inputs to
        the rolling window and exponential weighted window.
        default setting are stored in .../ref_data/ma_params.csv

        data_obj, object. Object returned from TimeSeries constructor

    Output: DataFrame with original series as well as moving averages
    """

    df = data_obj.timeseries
    df.columns = [data_obj.name]
    
    for i in list(range(len(window_params)-1)):
        window = ma_params.at[i,'window_length']
        min_periods = ma_params.at[i,'min_periods']
        half_life = ma_params.at[i,'half_life']
        col_name = data_obj.name+'_MA'+str(window)

        df[col_name] = df[data_obj.name].rolling(window=window,min_periods=min_periods).mean()

        col_name = data_obj.name+'_expMA'+str(window)

        df[col_name] = df[data_obj.name].ewm(halflife=half_life,min_periods=min_periods).mean()
            
    return df
        
        
def get_data_codes():
    """ Returns the data codes CSV in dataframe format.
    Useful for interrogating static data in a notebook
    """

    return data_codes


def ts_get(code, start, end, provider):
    """
    Get time series data from various providers
    Returns a dataframe object
    """
    
    if provider == 'quandl':
        ts = qd.get(
            code,
            start_date=start,
            end_date=end
        )
        if len(ts.columns) > 1: ts = pd.DataFrame(ts['Settle'])
    elif provider == 'fred':
        ts = pd.DataFrame(fred.get_series(series_id=code,
                                          observation_start=start,
                                          observation_end=end
                                          )
                          )
    
    return ts


def yield_curve(issuer='ge',
                maturities=[1, 2, 3, 4, 5, 7, 10, 15, 20, 30],
                start=dt(2019, 1, 1),
                end=dt.today(),
                unit='py',
                currency=False,
                asset_type=False,
                maturity_types=False):
    """ Create dataframe of bonds of different maturities

    maturities - array of integers
    start - datetime object
    end - datetime object
    unit - type of data. 'py' for par_yield, 'ry' for real_yield
           'be' for breakeven, 'zy' for zero_coupon_yield
           'pr' for price
    currency - my short code. defaults to issuer default ccy
    asset_type - my short code - defaults to issuer default asset type
    maturity_types - array of maturity types e.g. 'y' for each maturity
    """

    if currency is False:
        currency = issuers.at[issuer, 'currency']
    if asset_type is False:
        asset_type = issuers.at[issuer, 'asset_type']
    if maturity_types is False:
        maturity_types = ['y'] * len(maturities)

    for i, y in enumerate(maturities):
        # i for list position, y for maturity (i.e. list entry)
        code = (currency + issuer + asset_type + str(y)
                + maturity_types[i] + 'c' + unit)
        this_asset = TimeSeries(code, start, end)
        col_name = this_asset.name
        # if at first stage of iteration, need to create the dataframe
        if i == 0:
            df = pd.DataFrame(this_asset.timeseries, columns=[col_name])
        df[col_name] = this_asset.timeseries

    return df

def ts_releases_get(code, start=dt(1980,1,1), end=dt.today(),
                   revisions=[0],revs_from_last=[0], data_supplier='fred'):
    """Function to return dataframe for all releases of a particular datapoint. 
    
    Inputs:
        code, string. The code for the data point as defined in my database/CSV.
        start, datetime. Start date for data series.
        end, datetime. End date for data series. 
        revisions, list. List of revisions desired in output. [0] give original release. 
            [0,1] gives release and first revision. 
        rev_from_last, list. Gives revisions counted backwards from last revision.
            [0] give the last revision value and date. 
        data_supplier, string. Tells ts_releases_get which API to use.
    
    Output:
        DataFrame. Index is the date for the particular datapoint. Columns are a two-level. 
        First column shows how many releases there were of that data point. Then three groups of columns
        for values, release dates and "releases". "releases" is an integer, and shows which release is
        being shown. Useful for 0th last release, for example as it explicitly shows which release 
        the data is. E.g. is the last release the 3rd, 5th or 10th revision?
    """
    if data_supplier == 'fred':
        all_releases = fred.get_series_all_releases(code)
        df_revs = all_releases.groupby('date').apply(release_n, revisions=revisions,
                                                            revs_from_last=revs_from_last)
        df_revs.reset_index(level=1,drop=True,inplace=True)
    
    return df_revs
    
    
def release_n(df, revisions=[0], revs_from_last=[0]):
    """ Used in ts_releases_get as part of groupby().apply()
    
    Inputs:
        df, DataFrame. Grouped DataFrame which should be all data for a given datapoint. 
            The dataframe should have named columns: "realtime_start" corresponds to a release/revision
            data of that data point. "value" is the value of the data on that release/revision.
        revisions, list. List of revisions desired in output. [0] give original release. 
            [0,1] gives release and first revision. 
        rev_from_last, list. Gives revisions counted backwards from last revision.
            [0] give the last revision value and date. 
        revisions and rev_from_last can include empty list []
        
    Output:
        DataFrame with two-level index. Level 0 is the datapoint dates. Columns are a two-level. 
        First column shows how many releases there were of that data point. Then three groups of columns
        for values, release dates and "releases". "releases" is an integer, and shows which release is
        being shown. Useful for 0th last release, for example as it explicitly shows which release 
        the data is. E.g. is the last release the 3rd, 5th or 10th revision?
    """
    #create a revs list. This concatenates the input data and converts the "revs from last"
    #integers into the "revs from first" - so same basis as the revisions list
    revs = revisions + revs_from_last
    # create column names for the output DataFrame
    cols = ['e']*len(revs)
    for n, i in enumerate(revisions):
        cols[n] = f'rev_{i}'
        revs[n] = min(i, len(df)-1)
    for n, i in enumerate(revs_from_last):
        revs[n + len(revisions)] = max(0, len(df) - 1 - i)
        cols[n + len(revisions)] = f'rev_{i}th_last'
    # create output DataFrame

    columns = [['releases']+['values']*len(revs)+
                ['release_dates']*len(revs)+
                ['[CHECK!]_release_no']*len(revs),
                ['releases']+cols*3
              ]
    df_out = pd.DataFrame(np.zeros((1,1 + len(revs)*3)), columns = columns)
    df_out[('releases','releases')] = len(df)
    # Populate columns in output DataFrame - both release value and release date
    for n, i in enumerate(revs):
        if n==0 or i > revs[n-1]:
            df_out[('values',cols[n])] = df['value'].iloc[i]
            df_out[('release_dates',cols[n])] = df['realtime_start'].iloc[i]
            df_out[('[CHECK!]_release_no',cols[n])] = i + 1
        else:
            df_out[('values',cols[n])] = np.nan
            df_out[('release_dates',cols[n])] = np.nan
            df_out[('[CHECK!]_release_no',cols[n])] = i + 1
    return df_out

        