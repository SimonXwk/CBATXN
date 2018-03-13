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
    filename_pattern = '_'.join([bsb_number, account_number, '*', '*'])
    return os.path.join(folder, filename_pattern + '.csv')


def get_merged_csv(file_list, **kwargs):
    return pd.concat([pd.read_csv(f, **kwargs) for f in file_list], axis=0, ignore_index=True)


def search_in_series(data_series, query, **kwargs):
    return data_series.str.contains(query, **kwargs)


def extract_from_series(data_series, query, **kwargs):
    return data_series.str.extract(query, **kwargs)


def collect_data(account_number, bsb_number):

    # Find out which csv files to be collected
    file_list = glob.glob(get_csv_mask_in_folder(get_csv_folder(), bsb_number, account_number))

    # Collect data
    header_bank_date = Config.CSV_HEADER_CBA['BANKDATE']
    header_amount = Config.CSV_HEADER_CBA['AMOUNT']
    header_description = Config.CSV_HEADER_CBA['DESCRIPTION']
    header_balance = Config.CSV_HEADER_CBA['BALANCE']

    df = get_merged_csv(file_list, header=None, index_col=None)  # If file contains no header row, then you should explicitly pass header=None
    df.columns = [header_bank_date, header_amount, header_description, header_balance]

    # Process data : Preliminary
    df[header_bank_date] = pd.to_datetime(df[header_bank_date])
    df[header_amount] = pd.to_numeric(df[header_amount])
    df[header_description] = df[header_description].str.strip()

    # Process data : Find Features

    # Only one match group in parenthesis: Date Component; NA means the value date and the bank date are identical
    df['Value Date'] = pd.to_datetime(extract_from_series(df[header_description], 'value date: (\d+/\d+/\d+)', flags=re.IGNORECASE, expand=False)).fillna(df[header_bank_date])
    df['Cash Out'] = pd.to_numeric(extract_from_series(df[header_description], '.*cash *out *\$? *(\d+\.\d+|\d+)', flags=re.IGNORECASE, expand=False)) * (-1)
    df['Net'] = df[header_amount].fillna(0) - df['Cash Out'].fillna(0)

    df['Delayed'] = search_in_series(df[header_description], 'value date: ../../....', case=False, regex=True)

    df['Trf In'] = search_in_series(df[header_description], 'transfer *from', flags=re.IGNORECASE, regex=True)
    df['Trf Out'] = search_in_series(df[header_description], 'transfer *to', flags=re.IGNORECASE, regex=True)

    df['CashDep'] = search_in_series(df[header_description], 'cash dep*', flags=re.IGNORECASE, regex=True)
    df['Withdraw'] = search_in_series(df[header_description], 'wdl *', flags=re.IGNORECASE, regex=True)
    df['CashOut'] = search_in_series(df[header_description], '.*cash *out *\$? *(\d+\.\d+|\d+)', flags=re.IGNORECASE, regex=True)

    df['DC'] = search_in_series(df[header_description], 'direct credit*', flags=re.IGNORECASE, regex=True)
    df['DD'] = search_in_series(df[header_description], 'direct debit*', flags=re.IGNORECASE, regex=True)

    # df[(df['Trf In']) & (df['Trf Out']) & (df['DC']), (df['DD'])]
    print(df[(df['Trf In'] == False) & (df['Trf Out']) & (df['DC']), (df['DD'])])

    df.to_csv(os.path.join(get_csv_folder(), 'out.csv'), encoding='utf-8-sig')


if __name__ == '__main__':
    account = '10330550'
    bsb = '063115'
    collect_data(account, bsb)

