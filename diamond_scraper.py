#!/usr/bin/env python

import pandas as pd
import urllib3
import certifi
import os
import time
import datetime
import re
from bs4 import BeautifulSoup
from collections import namedtuple
from json import loads

diamond = namedtuple('diamond',['shape','carat','color','clarity','cut','depth','table','lab','lab_id','price','url','img_url','cert_url','vid_url','date'])

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        'accept' : '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
        'x-requested-with' : 'XMLHttpRequest'
    }
)   

def ja_row_parser(row):
    l = row.text.split('\n')
    img = '=IMAGE("{}")'.format(row.find_next('img')['src'])
    url = "https://www.jamesallen.com/" + re.sub(r'.*\(\'(.*)\'\).*', r'\1', row.find_next('input')['onclick'])
    cert = '=IMAGE("{}")'.format(row.find_next(lambda a:a.name == 'a' and 'certimg' in a.attrs)['certimg'])
    now = datetime.datetime.now().strftime("%x %X")
    return diamond(l[3],l[5],l[6],l[7],l[8],l[9],l[10],None,l[11],l[13],url,img,cert,None,now)

def get_jamesallen(shape,color_list,cut_list,clarity_list,min_carat=1.7,max_carat=1.8,price_min=1000,price_max=99999,pause=0,**kwargs):
    local = False
    if local:
        f = open('jamesallen.html', 'r')
        bs = BeautifulSoup(f.read(), 'html.parser')
    else:
        url = ('https://www.jamesallen.com/loose-diamonds/{shape}/'
        '?CaratFrom={min_carat:.2f}'
        '&CaratTo={max_carat:.2f}'
        '&Color={color_list}'
        '&Cut={cut_list}'
        '&Clarity={clarity_list}'
        '&PriceFrom={price_min}'
        '&PriceTo={price_max}'
        '&ViewsOptions=List'
        '&Polish=EX,ID'
        '&Symmetry=EX,ID'
        '&Flour=None,Negligible'
        '&Lab=GIA'
        )
        print url.format(**locals())
        r = http.request('get',url.format(**locals()))    
        bs = BeautifulSoup(r.data, 'html.parser')
    try:
        nresults = int(bs.find(attrs={'class':'nopVal'}).text)
    except:
        nresults = 0
    rows = bs.find_all(attrs={'data-item-type':'Diamond'})
    diamonds = map(ja_row_parser,rows)
    if nresults>12:
        min_carat = float(diamonds[-1].carat)+.01
        time.sleep(pause)
        diamonds += get_jamesallen(**locals())
    return diamonds

def get_yadav(**kwargs):
    url = ('https://www.yadavjewelry.com/diamond?clarity_max=6'
        '&clarity_min=5'
        '&color_max=20'
        '&color_min=19'
        '&cut_max=5'
        '&cut_min=5'
        '&cut_ui_max=5'
        '&cut_ui_min=4'
        '&depth_max=88'
        '&depth_min=43'
        '&depth_ui_max=88'
        '&depth_ui_min=43'
        '&fluor_max=6'
        '&fluor_min=6'
        '&lab_cert=GIA'
        '&labcreated=false'
        '&origin=all'
        '&polish_max=4'
        '&polish_min=4'
        '&price_max=14000'
        '&price_min=9000'
        '&price_ui_max=%24+14000'
        '&price_ui_min=9000'
        '&results=500'
        '&search_waiting=0'
        '&shape-checkbox='
        '&shape=RB'
        '&supplier_shipping_date='
        '&symmetry_max=4'
        '&symmetry_min=4'
        '&tablep_max=85'
        '&tablep_min=48'
        '&tablep_ui_max=85'
        '&tablep_ui_min=48'
        '&utf8=%E2%9C%93'
        '&weight_max=1.8'
        '&weight_min=1.5'
        '&weight_ui_max=1.8'
        '&weight_ui_min=1.5'
        '&width_max=20'
        '&width_min=3'
        '&width_ui_max=20'
        '&width_ui_min=3'
    )
    print url.format(**locals())
    return http.request('get',url.format(**locals())).data

def get_yadav_stock_details(url):
    print(url)
    content = http.request('get', url).data
    bs = BeautifulSoup(content, 'html.parser')
    cert_elem = bs.find(attrs={'id': 'cert-button'})
    vid_elem = bs.find(attrs={'id': 'vid-button'})
    cert_url = cert_elem['href'] if cert_elem else ''
    vid_url = vid_elem['href'] if vid_elem else ''
    if vid_url == '#videoModal':
        vid_url = bs.find(attrs={'id': 'videoModal'}).find('source')['src']
    return (cert_url, vid_url)

def scrape_yadav(outdir,pause=2):
    # https://www.yadavjewelry.com/natural-loose-diamonds/round-diamonds/excellent-signature_ideal-cut/si1-vs1-clarity/h-g-color
    # f = open(os.path.join(outdir,'yadav.json'), 'r').read()
    f = get_yadav()
    diamonds = []

    js = re.search(r'typeOfView == "list_view"(.*?)^[ ]+}', f, re.MULTILINE|re.DOTALL).group(1)
    table = re.search(r'<table.*table>', js).group(0)
    escaped = table.decode('string_escape').replace('\\','')
    ebs = BeautifulSoup(escaped, 'html.parser') #.replace('\n','')
    for row in ebs.find_all('tr'):
        element = row.find(attrs={'class': 'diamond-comparison-btn'})
        if element:
            stock_id = element['data-id']
            img = row.find('img')['src']
            columns = map(lambda x: x.text, row.find_all('td'))
            carat = re.sub(r'([0-9\.]+).*', r'\1', columns[2])
            shape = columns[1].lower()
            color = columns[3]
            clarity = columns[4]
            cut = columns[5]
            lab = columns[6]
            depth = columns[9]
            table = columns[10]
            price = columns[15]
            url = 'https://www.yadavjewelry.com/diamond/{}-diamond-{}-carat-{}-{}-yd{}'.format(shape, carat, color, clarity, stock_id)
            now = datetime.datetime.now().strftime("%x %X")
            (cert_url, vid_url) = get_yadav_stock_details(url)
            lab_id = re.search(r'[0-9]{10}', cert_url).group(0)
            diamonds.append(diamond(shape, carat, color, clarity, cut, depth, table, lab, lab_id, price, url, img, cert_url, vid_url, now))
    now = datetime.datetime.now()
    today = now.strftime('%s') # %m-%d-%Y

    f = os.path.join(outdir + '/yadav','{}.csv'.format(today))
    data = pd.DataFrame(diamonds, columns=diamond._fields)
    data.to_csv(f, mode='w', header=True, sep='\t')

def scrape_jamesallen(outdir,pause=2):
    ### james allen
    # shapes = [
    #     'emerald-cut',
    #     'princess-cut',
    #     'asscher-cut',
    #     'oval-cut',
    #     'radiant-cut',
    #     'pear-shaped',
    #     'heart-shaped',
    #     'marquise-cut',
    #     'cushion-cut',
    #     'round-cut',
    # ]
    # colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', ]
    # claritys = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF', 'FL']
    # cuts = ['Very%20Good', 'Ideal', 'Excellent', 'TrueHearts']
    shapes = [
        'round-cut',
    ]
    colors = ['G', 'H']
    claritys = ['SI1', 'VS2']
    cuts = ['Ideal', 'Excellent', 'TrueHearts']

    f = os.path.join(outdir,'james_allen.csv')
    first = True
    for s in shapes:
        diamonds = []
        for co in colors:
           for cl in claritys:
                for cu in cuts:
                    print('fetching for {s} {co} {cl} {cu}'.format(**locals()))
                    diamonds = get_jamesallen(s,co,cu,cl,pause=pause)
                    data = pd.DataFrame(diamonds, columns=diamond._fields)
                    if first:
                        data.to_csv(f, mode='w', header=True, sep='\t')
                    else:
                        data.to_csv(f, mode='a', header=False, sep='\t')
                    time.sleep(pause)

def scrape_bluenile(outdir,pageSize=500,startIndex=0,pause=3):
    # EC, AS, RD, PR, CU, HS, PS, OV, RA, MQ
    url = ('http://www.bluenile.com/api/public/diamond-search-grid/v2'
        '?country=USA'
        '&language=en-us'
        '&currency=USD'
        '&startIndex={i}'
        '&pageSize={pageSize}'
        '&shape=RD'
        '&sortColumn=price'
        '&sortDirection=asc'
        '&minCarat=1.72'
        '&maxCarat=1.89'
        '&minCut=Ideal'
        '&maxCut=Astor%20Ideal'
        '&minColor=H'
        '&maxColor=D'
        '&minClarity=SI1'
        '&maxClarity=FL'
        '&minPolish=EX'
        '&maxPolish=EX'
        '&minSymmetry=EX'
        '&maxSymmetry=EX'
        '&minFluorescence=None'
        '&maxFluorescence=None'
        '&hasVisualization=true'
        )
    f = os.path.join(outdir,'blue_nile.csv')
    i = startIndex
    count = 1
    while i<count:
        j = 0
        try:
            print(url.format(**locals()))
            r = http.request('get',url.format(**locals()))
            d = loads(r.data)
        except:
            if j>1:
                print r.data
                raise
            j += 1
            time.sleep(pause)
        count = d['countRaw']
        data = pd.DataFrame(d['results'])
        data = data.drop(['date', 'dateSet', 'hasVisualization', 'id', 'lxwRatio', 'myPickSelected', 'polish', 'shapeCode', 'shapeName', 'shipsInDays', 'shipsInDaysSet', 'skus'], axis=1)
        data = data.applymap(lambda cell: ''.join([str(x) for x in cell]))
        if i == 0:
            data.to_csv(f, mode='w', header=True, sep='\t', encoding='utf-8')
        else:
            data.to_csv(f, mode='a', header=False, sep='\t', encoding='utf-8')
        i += pageSize
        print "Retrived {i} of {count}".format(**locals())
        time.sleep(pause)

def main():
    #scrape_jamesallen(os.getcwd())
    #scrape_bluenile(os.getcwd())
    scrape_yadav(os.getcwd())

if __name__== "__main__":
    main()
