import pandas as pd
import urllib3
import certifi
import os
import time
from bs4 import BeautifulSoup
from collections import namedtuple
from json import loads

diamond = namedtuple('diamond',['shape','carat','color','clarity','cut','depth','table','lab','price'])

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'}
)                                

def ja_row_parser(row):
    l = row.text.split('\n')
    return diamond(l[3],l[5],l[6],l[7],l[8],l[9],l[10],l[11],l[13])

def get_jamesallen(shape,color_list,cut_list,clarity_list,min_carat=.05,max_carat=100.0,price_min=0,price_max=999999999,pause=0,**kwargs):
    url = 'https://www.jamesallen.com/loose-diamonds/{shape}/?CaratFrom={min_carat:.2f}&CaratTo={max_carat:.2f}&Color={color_list}&Cut={cut_list}&Clarity={clarity_list}&PriceFrom={price_min}&PriceTo={price_max}&ViewsOptions=List'
    print url.format(**locals())     
    r = http.request('get',url.format(**locals()))    
    bs = BeautifulSoup(r.data)       
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

def scrape_jamesallen(outdir,pause=2):

    ### james allen
    shapes = [
        'emerald-cut',
        'princess-cut',
        'asscher-cut',
        'oval-cut',
        'radiant-cut',
        'pear-shaped',
        'heart-shaped',
        'marquise-cut',
        'cushion-cut',
        'round-cut',
    ]
    colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', ]
    claritys = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF', 'FL']
    cuts = ['Very%20Good', 'Ideal', 'Excellent', 'TrueHearts']

    f = os.path.join(outdir,'james_allen.csv')
    for s in shapes:
        diamonds = []
        for co in colors:
           for cl in claritys:
                for cu in cuts:
                    diamonds = get_jamesallen(s,co,cu,cl,pause=pause)
                    data = pd.DataFrame(diamonds, columns=diamond._fields)
                    data.to_csv(f, mode='a', header=False)
                    time.sleep(pause)

def scrape_bluenile(outdir,pageSize=500,startIndex=0,pause=3):
    url = "http://www.bluenile.com/api/public/diamond-search-grid/v2?country=USA&language=en-us&currency=USD&startIndex={i}&pageSize={pageSize}&shape=EC&shape=AS&shape=RD&shape=PR&shape=CU&shape=HS&shape=PS&shape=OV&shape=RA&shape=MQ&sortColumn=price&sortDirection=asc"
    f = os.path.join(outdir,'blue_nile.csv')
    i = startIndex
    count = 1
    while i<count:   
        j = 0
        try:
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
        if i == 0:
            data.to_csv(f, mode='w', header=True)
        else:
            data.to_csv(f, mode='a', header=False)
        i += pageSize
        print "Retrived {i} of {count}".format(**locals())
        time.sleep(pause)

def main():
    #scrape_jamesallen(os.getcwd())
    #scrape_bluenile(os.getcwd())

if __name__=="__main__":
    main()
    
            
    


