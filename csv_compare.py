#!/usr/bin/env python
import pandas as pd
from datetime import timedelta, datetime

def main():
	now = datetime.now()
	day_ago = now - timedelta(days=1)
	file_today = "yadav-{}.csv".format(now.strftime('%m-%d-%Y'))
	file_yday  = "yadav-{}.csv".format(day_ago.strftime('%m-%d-%Y'))

	prev = pd.read_csv(file_yday, sep='\t')
	curr = pd.read_csv(file_today, sep='\t')

	curr = curr[~curr.url.isin(prev.url)]
	print(curr.url.to_dict())

if __name__== "__main__":
    main()
