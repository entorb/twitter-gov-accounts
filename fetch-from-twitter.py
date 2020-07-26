import os
import time
import csv
import requests  # for read_url_or_cachefile

# http://api.twittercounter.com?twitter_id=813286&apikey=[api_key]


def check_cache_file_available_and_recent(fname: str, max_age: int = 3600, verbose: bool = False) -> bool:
    b_cache_good = True
    if not os.path.exists(fname):
        if verbose:
            print(f"No Cache available: {fname}")
        b_cache_good = False
    if (b_cache_good and time.time() - os.path.getmtime(fname) > max_age):
        if verbose:
            print(f"Cache too old: {fname}")
        b_cache_good = False
    return b_cache_good


def read_url_or_cachefile(url: str, cachefile: str, request_type: str = 'get', payload: dict = {}, cache_max_age: int = 3600, verbose: bool = True) -> str:
    b_cache_is_recent = check_cache_file_available_and_recent(
        fname=cachefile, max_age=cache_max_age, verbose=verbose)
    if not b_cache_is_recent:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ',
        }
        if request_type == 'get':
            cont = requests.get(url, headers=headers).content
        elif request_type == 'post':
            cont = requests.post(url, headers=headers, data=payload).content
        with open(cachefile, mode='wb') as fh:
            fh.write(cont)
        cont = cont.decode('utf-8')
    else:
        with open(cachefile, mode='r', encoding='utf-8') as fh:
            cont = fh.read()
    return cont


def fetch_from_twitter(account: str, cachefilename: str, verbose=False) -> str:
    html = read_url_or_cachefile(url=f"https://twitter.com/{account}",
                                 cachefile=f"cache/{cachefilename}.html")
    return html


l_landkreise = []
with open('data/DE-Landkreise-in.csv', mode='r', encoding='utf-8') as fh:
    csv_reader = csv.DictReader(fh, dialect='excel', delimiter=";")
    for row in csv_reader:
        d = dict(row)
        if d['Twitter Account'] not in ("", "-"):
            d['Twitter URL'] = f"https://twitter.com/{d['Twitter Account']}"
            # print(
            #     f"{d['LK_Name']} ({d['LK_Type']})\t{d['Twitter Account']}")
        l_landkreise.append(d)

        # fetch_from_twitter(
        #     account=row['Twitter Account'], cachefilename=f"{row['LK_ID']} {row['LK_Name']} ({row['LK_Type']})")

l_columns = list(l_landkreise[0].keys())
l_columns_twitter = (
    'Twitter Account',
    'Twitter URL',
    'Twitter Name',
    'Twitter Follower',
    'Twitter Tweets'
)
for s in l_columns_twitter:
    if s not in l_columns:
        l_columns.append(s)


with open('data/DE-Landkreise-out.tsv', mode='w', encoding='utf-8', newline='\n') as fh:
    csvwriter = csv.DictWriter(
        fh, delimiter='\t', extrasaction='ignore', fieldnames=l_columns)
    csvwriter.writeheader()
    for d in l_landkreise:
        if d['Twitter Account'] not in ("", "-"):
            d['Twitter URL'] = f"https://twitter.com/{d['Twitter Account']}"
        csvwriter.writerow(d)
