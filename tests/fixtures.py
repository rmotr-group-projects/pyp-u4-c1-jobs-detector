import pickle
import responses
from os import path
import re

PICKLEFILE = path.join(path.dirname(path.abspath(__file__)), 'fixtures.pickle')
FIXTURE_PATH = path.join(path.dirname(path.abspath(__file__)), 'fixtures')

def load_fixtures():
    with open(PICKLEFILE, 'rb') as p:
        fixtures = pickle.load(p)

    for url, filepath in fixtures:
        with open(path.join(FIXTURE_PATH, filepath), 'rb') as f:
            content = f.read()
        responses.add(responses.GET,
                      re.compile(re.escape(url)),
                      body=content, status=200,
                      content_type='application/json')