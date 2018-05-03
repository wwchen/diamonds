#!/usr/bin/env python
import pandas as pd
import os
from datetime import timedelta, datetime
import urllib
import re

def extract_gia_ids(list):
	return map(lambda m: m[:10], filter(lambda n: len(n[:10]) == 10 and n[:10].isdigit(), list))

def cmp_new_rows(basefn, currfn, key):
	base = pd.read_csv(basefn, sep='\t')
	curr = pd.read_csv(currfn, sep='\t')
	return curr[~curr[key].isin(base[key])]

def epoch_str(epoch, strftime = '%m-%d-%Y %H:%M'):
	return datetime.fromtimestamp(int(epoch)).strftime(strftime)

def diff_latest_csvs(root_dir):
	"""assumes the filenames are the epoch string
	assumes root_dir exists and ends with slash
	assumes there's more than two files"""
	filenames = os.listdir(root_dir)
	filenames.sort(reverse=True)
	head_fn, base_fn = filenames[:2]
	head_path, base_path = map(lambda fn: root_dir + fn, filenames[:2])
	print('comparing base {} with head {}'.format(epoch_str(base_fn[:10]), epoch_str(head_fn[:10])))
	return cmp_new_rows(base_path, head_path, 'lab_id')

def filter_rows_by_remained_downloads(tmp_dir, dataframe, url_colname, key_colname):
	fstruct = lambda p: re.search('(.*)\.(.+)$', os.path.basename(p)).groups()
	for idx, row in dataframe.iterrows():
		url, key = row[url_colname], row[key_colname]
		if pd.isnull(url):
			continue
		path = '{}{}.{}'.format(tmp_dir, key, fstruct(url)[1])
		if not os.path.exists(path):
			print('downloading {} to {}'.format(url, path))
			urllib.urlretrieve(url, path)
	raw_input('After sorting through the files in {}, press Enter to continue...'.format(tmp_dir))
	keys = map(lambda fpath: fstruct(fpath)[0], os.listdir(tmp_dir))
	for i in os.listdir(tmp_dir):
		os.remove(tmp_dir + i)
	return dataframe[dataframe[key_colname].isin(keys)]


def main():
	filtered = diff_latest_csvs(os.getcwd() + '/bbucutting/')
	filtered_fn = 'bbucutting-filtered.csv'
	filtered.to_csv(open(filtered_fn, 'w'), mode='w', header=False, sep='\t')
	########
	# now = datetime.now()
	# day_ago = now - timedelta(days=1)
	# file_today = "yadav/{}.csv".format(now.strftime('%m-%d-%Y'))
	# file_yday  = "yadav-{}.csv".format(day_ago.strftime('%m-%d-%Y'))
	gia_dir = os.getcwd() + '/yadav-cert/'
	filtered = diff_latest_csvs(os.getcwd() + '/yadav/')
	if len(filtered) == 0:
		print('no changes since last file')
		return

	filtered = filter_rows_by_remained_downloads(gia_dir, filtered, 'img_url', 'lab_id')
	filtered = filter_rows_by_remained_downloads(gia_dir, filtered, 'cert_url', 'lab_id')

	f = open('yadav-filtered.csv', 'w')
	filtered.to_csv(f, mode='w', header=False, sep='\t')

	for i in os.listdir(gia_dir):
		os.remove(gia_dir + i)



if __name__== "__main__":
    main()
