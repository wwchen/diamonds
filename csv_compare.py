#!/usr/bin/env python
import pandas as pd
import os
from datetime import timedelta, datetime
import urllib
import re

def main():
	# now = datetime.now()
	# day_ago = now - timedelta(days=1)
	# file_today = "yadav/{}.csv".format(now.strftime('%m-%d-%Y'))
	# file_yday  = "yadav-{}.csv".format(day_ago.strftime('%m-%d-%Y'))
	root_dir = os.getcwd() + '/yadav/'
	gia_dir = os.getcwd() + '/yadav-cert/'
	filenames = os.listdir(root_dir)
	filenames.sort(reverse=True)

	prev = pd.read_csv(root_dir + filenames[1], sep='\t')
	curr = pd.read_csv(root_dir + filenames[0], sep='\t')

	print('comparing {} with {}'.format(filenames[1], filenames[0]))

	filtered = curr[~curr.lab_id.isin(prev.lab_id)]
	for idx, row in filtered.iterrows():
		url = row.cert_url
		path = gia_dir + os.path.basename(url)
		if not os.path.exists(path):
			print('downloading {}'.format(url))
			urllib.urlretrieve(url, path)
		else:
			print('skipping downloading {}'.format(url))

	raw_input('After sorting through the GIA certs, press Enter to continue...')

	ids = extract_gia_ids(os.listdir(gia_dir))
	filtered = filtered[filtered.lab_id.isin(ids)]
	
	for i in os.listdir(gia_dir):
		os.remove(gia_dir + i)

	for idex, row in filtered.iterrows():
		url = row.img_url
		path = gia_dir + str(row.lab_id) + '.jpg'
		if not os.path.exists(path):
			print('downloading {}'.format(url))
			urllib.urlretrieve(url, path)
		else:
			print('skipping downloading {}'.format(url))
		
	raw_input('After sorting through the diamond images, press Enter to continue...')

	ids = extract_gia_ids(os.listdir(gia_dir))
	filtered = filtered[filtered.lab_id.isin(ids)]

	f = open('yadav-filtered.csv', 'w')
	filtered.to_csv(f, mode='w', header=False, sep='\t')

	for i in os.listdir(gia_dir):
		os.remove(gia_dir + i)

def extract_gia_ids(list):
	return map(lambda m: m[:10], filter(lambda n: len(n[:10]) == 10 and n[:10].isdigit(), list))

if __name__== "__main__":
    main()
