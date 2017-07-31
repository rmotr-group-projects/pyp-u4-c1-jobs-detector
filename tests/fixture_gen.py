import requests
from os import path
import pickle

BASE_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty"
POST_ID = 11814828
FILE = '{}.json'
FIXTURE_PATH = path.join(path.dirname(path.abspath(__file__)), 'fixtures')


def get_fixture(post_id, fixtures):
    url = BASE_URL.format(post_id)
    r = requests.get(url)

    r.raise_for_status()

    filepath = path.join(FIXTURE_PATH, FILE.format(post_id))
    with open(filepath, 'wb') as out:
        out.write(r.content)

    fixtures.append((url, filepath))

    return r.json()

fixtures = []

root = get_fixture(POST_ID, fixtures)

for post in root['kids']:
    get_fixture(post, fixtures)

picklefile = path.join(path.dirname(FIXTURE_PATH), 'fixtures.pickle')
with open(picklefile, 'wb') as p:
    pickle.dump(fixtures, p)