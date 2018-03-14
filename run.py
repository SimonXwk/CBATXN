import os
import glob
import re
import pandas as pd

from Config import Config


def get_csv_folder():
    csv_folder = Config.CSV_DIR
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    return csv_folder


def get_csv_mask_in_folder(folder, bsb_number, account_number):
    filename_pattern = '_'.join([bsb_number, account_number, '*'])
    return os.path.join(folder, filename_pattern + '.csv')


def get_merged_csv(file_list, **kwargs):
    return pd.concat([pd.read_csv(f, **kwargs) for f in file_list], axis=0, ignore_index=True)  # Merge from Top-Down(axis0) and ignore indexes when merging


def search_in_series(data_series, query, **kwargs):
    return data_series.str.contains(query, **kwargs)


def collect_data(account_number, bsb_number):
    """ using account number and bsb number to identify and collect files with these information in the file names (pattern defined in get_csv_mask_in_folder())
    :param account_number: Australian Bank Account Number(no space)
    :param bsb_number: Australian Bank 6 digit BSB code(no space: xxy zzz)
    :return: CSV file under the folder predefined in the Config py file
    """

    # Find out which csv files to be collected, returning a list of file names
    file_list = glob.glob(get_csv_mask_in_folder(get_csv_folder(), bsb_number, account_number))
    print('Number of files to be collected : {}\n{}'.format(len(file_list), file_list))

    # Predefine(Config) the column names in the source csv files (assuming they all have the same structure since they come from the same Bank)
    header_bank_date = Config.CSV_HEADER_CBA['BANKDATE']
    header_amount = Config.CSV_HEADER_CBA['AMOUNT']
    header_description = Config.CSV_HEADER_CBA['DESCRIPTION']
    header_balance = Config.CSV_HEADER_CBA['BALANCE']

    # Collecting information and merge all to one Pandas DataFrame
    df = get_merged_csv(file_list, header=None, index_col=None)  # If file contains no header row, then you should explicitly pass header=None
    df.columns = [header_bank_date, header_amount, header_description, header_balance]
    print('\nRaw Data Format : {}\n{}'.format(df.shape, df.dtypes))

    # Cleaning Raw Data
    # Series.astype would not convert things that can not be converted to while pandas.to_datetime(Series) can (NaN).
    df[header_bank_date] = pd.to_datetime(df[header_bank_date], format='%d/%m/%Y')  # Convert to datetime value
    df[header_amount] = pd.to_numeric(df[header_amount]).astype('float')  # Convert to numeric value
    df[header_balance] = pd.to_numeric(df[header_balance]).astype('float')  # Convert to numeric value
    df[header_description] = df[header_description].str.strip()  # Trimming
    print('\nNew Data Format : {}\n{}'.format(df.shape, df.dtypes))

    # Creating New Value Columns by using Series.str.extract(pat, flags=0, expand=None)
    # :param pat : put only one pair of parenthesis for match group in order to extract this one value
    # :param flags : re.IGNORECASE, ignore case when using RE matching;
    # :param expand : False : return Series; True: return DataFrame
    df['ValueDate'] = pd.to_datetime(
        df[header_description].str.extract('.*Value +Date:? *([0,1,2,3]?[0-9]\/[0,1]?[0-9]\/[0-9]?[0-9]?[0-9]{2})', flags=re.IGNORECASE, expand=False)
        , format='%d/%m/%Y',).fillna(df[header_bank_date])  # Date Component; NA means the value date and the bank date are identical
    df['DaysWait'] = (df[header_bank_date] - df['ValueDate']).astype('timedelta64[D]')

    df['CashOut'] = ((-1) * pd.to_numeric(df[header_description].str.extract('.*cash *out *\$? *(\d+\.\d+|\d+)', flags=re.IGNORECASE, expand=False))).astype('float')
    df['Net'] = (df[header_amount].fillna(0) - df['CashOut'].fillna(0)).astype('float')

    # Creating Dummy Columns by using Series.str.contains(pat, case=True, flags=0, na=nan, regex=True)
    # :param case :  boolean,  If True, case sensitive
    # :param na : default NaN, fill value for missing values
    # :param regex : If True use re.search, otherwise use Python in operator
    df['PendingTxn'] = search_in_series(df[header_description], '.*value +date:? *[0,1,2,3]?\d\/[0,1]?\d\/\d?\d?\d{2}', case=False)
    df['CCTxn'] = search_in_series(df[header_description], '.*card +.*\d{4}.*', case=False)

    # Mutual Exclusive Categorical Information
    series_trf_in = search_in_series(df[header_description], '^transfer *from', case=False)
    series_trf_out = search_in_series(df[header_description], '^transfer *to', case=False)
    series_cash_dep = search_in_series(df[header_description], '.*cash +dep.*', case=False)
    series_withdraw = search_in_series(df[header_description], '^wdl *', case=False)
    series_dd = search_in_series(df[header_description], '.*direct credit.*', case=False)
    series_dc = search_in_series(df[header_description], '.*direct debit.*', case=False)

    df.loc[series_trf_in, 'TxnCategory'] = 'Transfer In'
    df.loc[series_trf_out, 'TxnCategory'] = 'Transfer Out'
    df.loc[series_cash_dep, 'TxnCategory'] = 'Cash Deposit'
    df.loc[series_withdraw, 'TxnCategory'] = 'Withdraw'
    df.loc[series_dd, 'TxnCategory'] = 'Direct Credit'
    df.loc[series_dc, 'TxnCategory'] = 'Direct Debit'
    df.loc[df['TxnCategory'].isna(), 'TxnCategory'] = 'Expense'
    df['TxnCategory'] = df['TxnCategory'].astype('category')

    # df['Exp'] = df[(df['TrfIn']==False) & (df['TrfIn']==False)]

    # df[(df['Trf In']) & (df['Trf Out']) & (df['DC']), (df['DD'])]
    # print(df[(df['Trf In'] == False) & (df['Trf Out']) & (df['DC']), (df['DD'])])

    print('\nFinal Data Format : {}\n{}'.format(df.shape, df.dtypes))
    df.to_csv(os.path.join(get_csv_folder(), 'out.csv'), encoding='utf-8-sig')


if __name__ == '__main__':
    account = '10330550'
    bsb = '063115'
    collect_data(account, bsb)

