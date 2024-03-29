#!/usr/bin/env python3
"""
Fetch data from Twitter API.
"""
import csv
import datetime
import json
import os
import time
from configparser import ConfigParser

import requests  # for read_url_or_cachefile

# TODO: replace index.html a static page and fill update date via javascript, instead of re-generation the file on each script run.

if not os.path.isdir("cache"):
    os.mkdir("cache")


def request_url(
    url: str,
    request_type: str = "get",
    payload: dict[str, str] | None = None,
) -> dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Authorization": "Bearer " + d_config["bearer-token"],
    }
    payload = payload or {}
    if request_type == "get":
        r = requests.get(url, headers=headers)
    elif request_type == "post":
        r = requests.post(url, headers=headers, data=payload)
    else:
        raise ValueError
        exit()
    # print(f"Status={r.status_code}")
    cont = r.content
    d_json = json.loads(cont.decode("utf-8"))
    assert r.status_code == 200, f"ERROR: status={r.status_code} cont={d_json}"
    return d_json


def fetch_user_metadata(username: str) -> dict[str, str]:
    try:
        d = request_url(
            url=f"https://api.twitter.com/1.1/users/show.json?screen_name={username}",
        )
    except (AssertionError) as error:
        d = {}
        print(error)
    return d


def fetch_user_metadata_from_cache_or_web(username: str) -> dict[str, str]:
    cache_file = f"cache/{username}.json"
    if check_cache_file_available_and_recent(fname=cache_file):
        with open(file=cache_file, encoding="utf-8") as fh:
            d_json = json.load(fh)
    else:
        d_json = fetch_user_metadata(username)
        with open(cache_file, mode="w", encoding="utf-8", newline="\n") as fh:
            json.dump(
                d_json,
                fh,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
    return d_json


def check_cache_file_available_and_recent(
    fname: str,
    max_age: int = 3600,
    verbose: bool = False,
) -> bool:
    b_cache_good = True
    if not os.path.exists(fname):
        if verbose:
            print(f"No Cache available: {fname}")
        b_cache_good = False
    if b_cache_good and time.time() - os.path.getmtime(fname) > max_age:
        if verbose:
            print(f"Cache too old: {fname}")
        b_cache_good = False
    return b_cache_good


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
config.read("api-keys.ini", encoding="utf-8")
d_config = {"bearer-token": config.get("API", "bearer-token")}
# d_config['api-key'] = config.get('API', 'api-key')
# d_config['api-secret-key'] = config.get('API', 'api-secret-key')

# read input data
l_landkreise: list[dict[str, str]] = []
with open("data/DE-Landkreise-in.csv", encoding="utf-8") as fh:
    csv_reader = csv.DictReader(fh, dialect="excel", delimiter=",")
    for row in csv_reader:
        d = dict(row)
        l_landkreise.append(d)

        # download_from_twitter(
        #     account=d['Twitter Account'], cachefilename=f"{d['LK_ID']} {d['LK_Name']} ({d['LK_Type']})")

# append twitter columns to columns of input file
l_columns = list(l_landkreise[0].keys())
l_columns_twitter = (
    "Twitter Account",
    "Twitter URL",
    "Twitter Name",
    "Twitter Description",
    "Twitter Follower",
    "Twitter Following",
    "Twitter Tweets",
    "Twitter Location",
    "Twitter ID",
)
for s in l_columns_twitter:
    if s not in l_columns:
        l_columns.append(s)

# fetch from Twitter API
for d in l_landkreise:
    if d["Twitter Account"] == "?" or d["Twitter Account"] == "-":
        continue
    print(d["Twitter Account"])
    d["Twitter URL"] = f"https://twitter.com/{d['Twitter Account']}"
    d_twitter_user_meta_data = fetch_user_metadata_from_cache_or_web(
        d["Twitter Account"],
    )
    if len(d_twitter_user_meta_data) > 0:
        d["Twitter ID"] = d_twitter_user_meta_data["id"]
        d["Twitter Name"] = d_twitter_user_meta_data["name"]
        d["Twitter Tweets"] = d_twitter_user_meta_data["statuses_count"]
        d["Twitter Follower"] = d_twitter_user_meta_data["followers_count"]
        d["Twitter Following"] = d_twitter_user_meta_data["friends_count"]
        d["Twitter Location"] = d_twitter_user_meta_data["location"]
        # d["Twitter Description"] = d_twitter_user_meta_data['description']
        # if 'profile_location' in d_twitter_user_meta_data and d_twitter_user_meta_data['profile_location'] and 'full_name' in d_twitter_user_meta_data['profile_location']:
        #     d["Twitter Location"] = d_twitter_user_meta_data['profile_location']['full_name']

# Export as JSON (in dir docs for tabulator JS table)
with open(
    "docs/DE-Landkreise-out.json",
    mode="w",
    encoding="utf-8",
    newline="\n",
) as fh:
    json.dump(
        l_landkreise,
        fh,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )

# Export as CSV
with open("data/DE-Landkreise-out.csv", mode="w", encoding="utf-8", newline="\n") as fh:
    csvwriter = csv.DictWriter(
        fh,
        delimiter=",",
        extrasaction="ignore",
        fieldnames=l_columns,
    )
    csvwriter.writeheader()
    for d in l_landkreise:
        csvwriter.writerow(d)

# Export as static HTML
date = datetime.date.today().strftime("%d.%m.%y")
with open("docs/index.html", mode="w", encoding="utf-8", newline="\n") as fh:
    fh.write(
        f"""<!doctype html>
<html lang="de">
<head>
    <title>Liste der Twitter Accounts der Deutschen Stadtkreise und Landkreise</title>
    <meta charset="utf-8">
    <meta name="author" content="Dr. Torben Menke">
    <link rel="stylesheet" href="https://entorb.net/style.css" />
    <script src="./tab.js"></script>
    <!-- Polyfiles for IE, suggested by Tabulator : http://tabulator.info/docs/4.6/browsers#ie -->
    <script src="https://entorb.net/COVID-19-coronavirus/js/tabulator-polyfill.min.js"></script>
    <script src="https://entorb.net/COVID-19-coronavirus/js/tabulator-fetch.umd.js"></script>
    <!-- Tabulator -->
    <link href="https://entorb.net/COVID-19-coronavirus/js/tabulator.min.css" rel="stylesheet">
    <script src="https://entorb.net/COVID-19-coronavirus/js/tabulator-4.6.min.js"></script>
</head>

<body>

<p>Ab dem 09.02.2023 ist die Verwendung der API nicht mehr kostenlos, siehe <a href="https://twitter.com/TwitterDev/status/1621026986784337922">Tweet</a>. Daher werde ich die Daten nicht mehr aktualisieren.
</p>
<h1>Liste der Twitter Accounts der Deutschen Stadtkreise und Landkreise</h1>
<p>
Dies Liste ist noch nicht komplett. Korrekturen und Ergänzungen bitte direkt via GitHub Pull Request in die Datei <a href="https://github.com/entorb/twitter-gov-accounts/blob/master/data/DE-Landkreise-in.csv">data/DE-Landkreise-in.csv</a> einpflegen. Quelltext des Auswerteskriptes ist <a href="https://github.com/entorb/twitter-gov-accounts" target="_blank">hier</a> zu finden. Zeile anklicken um Twitter Profil zu öffnen.
</p>
<p>Stand: {date}</p>"""
        + """
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
""",
    )
