
# import twitter
from configparser import ConfigParser
import requests
import json


config = ConfigParser(interpolation=None)
config.read('api-keys.ini', encoding='utf-8')
d_config = {}
d_config['api-key'] = config.get('API', 'api-key')
d_config['api-secret-key'] = config.get('API', 'api-secret-key')
d_config['bearer-token'] = config.get('API', 'bearer-token')
# print(d_config)

# twitter.Api(bearer_token=d_config['bearer-token'])

# api = twitter.Api(consumer_key=[consumer key],
#                   consumer_secret=[consumer secret],
#                   access_token_key=[access token],
#                   access_token_secret=[access token secret])


def request_url(url: str, request_type: str = 'get', payload: dict = {}) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ',
        'Authorization': 'Bearer ' + d_config['bearer-token']
    }
    if request_type == 'get':
        r = requests.get(url, headers=headers)
    elif request_type == 'post':
        r = requests.post(url, headers=headers, data=payload)
    print(f"Status={r.status_code}")
    cont = r.content
    d_json = json.loads(cont.decode('utf-8'))
    assert r.status_code == 200, f"ERROR: status={r.status_code} cont={d_json}"
    return d_json


def fetch_user_metadata(username: str) -> dict:
    return request_url(
        url=f'https://api.twitter.com/1.1/users/show.json?screen_name={username}')


d = fetch_user_metadata(username='entorb')
print(d)
