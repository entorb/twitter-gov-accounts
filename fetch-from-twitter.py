import os
import datetime
import time
import csv
import requests  # for read_url_or_cachefile
from configparser import ConfigParser
import json

# http://api.twittercounter.com?twitter_id=813286&apikey=[api_key]


def request_url(url: str, request_type: str = 'get', payload: dict = {}) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ',
        'Authorization': 'Bearer ' + d_config['bearer-token']
    }
    if request_type == 'get':
        r = requests.get(url, headers=headers)
    elif request_type == 'post':
        r = requests.post(url, headers=headers, data=payload)
    # print(f"Status={r.status_code}")
    cont = r.content
    d_json = json.loads(cont.decode('utf-8'))
    assert r.status_code == 200, f"ERROR: status={r.status_code} cont={d_json}"
    return d_json


def fetch_user_metadata(username: str) -> dict:
    try:
        d = request_url(
            url=f'https://api.twitter.com/1.1/users/show.json?screen_name={username}')
    except(AssertionError) as error:
        d = {}
        print(error)
    return d


# def check_cache_file_available_and_recent(fname: str, max_age: int = 3600, verbose: bool = False) -> bool:
#     b_cache_good = True
#     if not os.path.exists(fname):
#         if verbose:
#             print(f"No Cache available: {fname}")
#         b_cache_good = False
#     if (b_cache_good and time.time() - os.path.getmtime(fname) > max_age):
#         if verbose:
#             print(f"Cache too old: {fname}")
#         b_cache_good = False
#     return b_cache_good


# def read_url_or_cachefile(url: str, cachefile: str, request_type: str = 'get', payload: dict = {}, cache_max_age: int = 3600, verbose: bool = True) -> str:
#     b_cache_is_recent = check_cache_file_available_and_recent(
#         fname=cachefile, max_age=cache_max_age, verbose=verbose)
#     if not b_cache_is_recent:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ',
#         }
#         if request_type == 'get':
#             cont = requests.get(url, headers=headers).content
#         elif request_type == 'post':
#             cont = requests.post(url, headers=headers, data=payload).content
#         with open(cachefile, mode='wb') as fh:
#             fh.write(cont)
#         cont = cont.decode('utf-8')
#     else:
#         with open(cachefile, mode='r', encoding='utf-8') as fh:
#             cont = fh.read()
#     return cont


# def download_from_twitter(account: str, cachefilename: str, verbose=False) -> str:
#     html = read_url_or_cachefile(url=f"https://twitter.com/{account}",
#                                  cachefile=f"cache/{cachefilename}.html")
#     return html
config = ConfigParser(interpolation=None)
config.read('api-keys.ini', encoding='utf-8')
d_config = {}
# d_config['api-key'] = config.get('API', 'api-key')
# d_config['api-secret-key'] = config.get('API', 'api-secret-key')
d_config['bearer-token'] = config.get('API', 'bearer-token')

# read input data
l_landkreise = []
with open('data/DE-Landkreise-in.csv', mode='r', encoding='utf-8') as fh:
    csv_reader = csv.DictReader(fh, dialect='excel', delimiter=",")
    for row in csv_reader:
        d = dict(row)
        l_landkreise.append(d)

        # download_from_twitter(
        #     account=d['Twitter Account'], cachefilename=f"{d['LK_ID']} {d['LK_Name']} ({d['LK_Type']})")

# append twitter columns to columns of input file
l_columns = list(l_landkreise[0].keys())
l_columns_twitter = (
    'Twitter Account',
    'Twitter URL',
    'Twitter Name',
    'Twitter Description',
    'Twitter Follower',
    'Twitter Following',
    'Twitter Tweets',
    'Twitter Location',
    'Twitter ID'

)
for s in l_columns_twitter:
    if s not in l_columns:
        l_columns.append(s)

# fetch from Twitter API
for d in l_landkreise:
    if d["Twitter Account"] == "?" or d["Twitter Account"] == "-":
        continue
    print(d['Twitter Account'])
    d["Twitter URL"] = f"https://twitter.com/{d['Twitter Account']}"
    d_twitter_user_meta_data = fetch_user_metadata(d['Twitter Account'])
    if len(d_twitter_user_meta_data) > 0:
        d["Twitter ID"] = d_twitter_user_meta_data['id']
        d["Twitter Name"] = d_twitter_user_meta_data['name']
        d["Twitter Tweets"] = d_twitter_user_meta_data['statuses_count']
        d["Twitter Follower"] = d_twitter_user_meta_data['followers_count']
        d["Twitter Following"] = d_twitter_user_meta_data['friends_count']
        d["Twitter Location"] = d_twitter_user_meta_data['location']
        d["Twitter Description"] = d_twitter_user_meta_data['description']
        # if 'profile_location' in d_twitter_user_meta_data and d_twitter_user_meta_data['profile_location'] and 'full_name' in d_twitter_user_meta_data['profile_location']:
        #     d["Twitter Location"] = d_twitter_user_meta_data['profile_location']['full_name']

# Export as JSON (in dir docs for tabulator JS table)
with open('docs/DE-Landkreise-out.json', mode='w', encoding='utf-8', newline='\n') as fh:
    json.dump(l_landkreise, fh, ensure_ascii=False, sort_keys=True)

# Export as CSV
with open('data/DE-Landkreise-out.csv', mode='w', encoding='utf-8', newline='\n') as fh:
    csvwriter = csv.DictWriter(
        fh, delimiter=',', extrasaction='ignore', fieldnames=l_columns)
    csvwriter.writeheader()
    for d in l_landkreise:
        csvwriter.writerow(d)

# Export as static HTML
date = datetime.date.today().strftime("%d.%m.%y")
with open('docs/index.html', mode='w', encoding='utf-8', newline='\n') as fh:
    fh.write(f"""<!doctype html>
<html lang="de">
<head>
    <title>Liste der Twitter Accounts der Deutschen Stadtkreise und Landkreise</title>
    <meta charset="utf-8">
    <meta name="author" content="Dr. Torben Menke">
    <link rel="stylesheet" href="https://entorb.net/style.css" />
    <script src="./tab.js"></script>
    <!-- Polyfiles for IE, suggested by Tabulator : http://tabulator.info/docs/4.6/browsers#ie -->
    <script src="https://entorb.net/COVID-19-coronavirus/tabulator/polyfill.min.js"></script>
    <script src="https://entorb.net/COVID-19-coronavirus/tabulator/fetch.umd.js"></script>
    <!-- Tabulator -->
    <link href="https://entorb.net/COVID-19-coronavirus/tabulator/tabulator.min.css" rel="stylesheet">
    <script src="https://entorb.net/COVID-19-coronavirus/tabulator/tabulator-4.6.min.js"></script>
</head>

<body>
<h1>Liste der Twitter Accounts der Deutschen Stadtkreise und Landkreise</h1>
<p>
Dies Liste ist noch nicht komplett. Korrekturen und Ergänzungen bitte direkt via GitHub Pull Request in die Datei <a href="https://github.com/entorb/twitter-gov-accounts/blob/master/data/DE-Landkreise-in.csv">data/DE-Landkreise-in.csv</a> einpflegen.
</p>
<p>Stand: {date}</p>"""
             +
             """
    <div id="table-de-districts"></div>
    <script>
        // variables
        const promises = []; // array of promises for async fetching
        // ASync JQuery fetching
        function fetch_table_data() {
            table.setData("https://entorb.github.io/twitter-gov-accounts/DE-Landkreise-out.json", {}, "get")
        }
        // define and populate table
        var table = defineTable();
        promises.push(fetch_table_data());
    </script>
</body>\n</html>
""")
# +
# """
# <table border="1" cellpadding="2" cellspacing="0">
# <tr>
# <th>Name</th>
# <th>Einwohner</th>
# <th>Bundesland</th>
# <th>Twitter Account</th>
# <th>Tweets</th>
# <th>Follower</th>
# </tr>
# """)
#     rowcount = 0
#     for d in l_landkreise:
#         rowcount += 1
#         fh.write(
#             f"""<tr class="r{1 + rowcount % 2}"><td>{d['LK_Name']} ({d['LK_Type']})</td><td>{d['Population']}</td><td>{d['BL_Name']}</td>""")
#         if 'Twitter ID' in d:
#             fh.write(
#                 f"""<td><a href="{d['Twitter URL']}" target="_blank">{d['Twitter Account']}</a></td>""")
#             fh.write(
#                 f"<td>{d['Twitter Tweets']}</td><td>{d['Twitter Follower']}</td></tr>\n")
#         else:
#             fh.write(f"<td>{d['Twitter Account']}</td>")
#             fh.write("<td>&nbsp;</td><td>&nbsp;</td></tr>\n")
#     fh.write("</table>\n</body>\n</html>")
