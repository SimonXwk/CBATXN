# Default Configuration (inheriting from object is not necessary in python3)
class Config(object):
	CSV_DIR = 'CSV'

	CSV_HEADER_CBA = {
		'BANKDATE': 'Bank Date',
		'AMOUNT': 'Amount',
		'DESCRIPTION': 'Description',
		'BALANCE': 'Balance'
	}

	AUSTRALIAN_BANK_CODE = {
		'01': {'CODE': 'ANZ', 'NAME': 'Australia and New Zealand Banking Group Limited', 'HEAD': None},
		'03': {'CODE': 'WPC', 'NAME': 'Westpac Banking Corporation', 'HEAD': None},
		'06': {'CODE': 'CBA', 'NAME': 'Commonwealth Bank of Australia', 'HEAD': None},
		'08': {'CODE': 'NAB', 'NAME': 'National Australia Bank', 'HEAD': None},
		'09': {'CODE': 'RBA', 'NAME': 'BankSA', 'HEAD': '03'},
		'10': {'CODE': 'BSA', 'NAME': 'Reserve Bank of Australia', 'HEAD': None},
		'12': {'CODE': 'BQL', 'NAME': 'Bank of Queensland', 'HEAD': None},
		'19': {'CODE': 'BOM', 'NAME': 'Bank of Melbourne', 'HEAD': '03'},
		'55': {'CODE': 'BML', 'NAME': 'Bank of Melbourne', 'HEAD': '03'},
		'30': {'CODE': 'BWA', 'NAME': 'Bankwest', 'HEAD': '06'}
	}

	AUSTRALIAN_STATE_CODE = {
		'02': {'CODE': 'NSW', 'NAME': ''},
		'03': {'CODE': 'VIC', 'NAME': ''},
		'04': {'CODE': 'QLD', 'NAME': ''},
		'05': {'CODE': 'SA', 'NAME': ''},
		'06': {'CODE': 'WA', 'NAME': ''},
		'07': {'CODE': 'TAS', 'NAME': ''}
	}

