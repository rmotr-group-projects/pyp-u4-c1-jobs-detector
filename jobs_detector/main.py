import click
import requests
from os import path
import json
import pickle
import xml.etree.ElementTree as ET

from jobs_detector import settings
from jobs_detector.exceptions import *

DEFAULT_KEYWORDS = [
    
    'remote', 'postgres', 'python', 'javascript', 'react', 'pandas'
]
BASE_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty"

@click.group()
def jobs_detector():
    # Leave this function alone
    pass


@jobs_detector.command()
@click.option('-i', '--post-id', type=str, required=True)
@click.option('-k', '--keywords', type=str, default=','.join(DEFAULT_KEYWORDS))
@click.option('-c', '--combinations', type=str,
              callback=lambda _, __, x: x.split(',') if x else x)
@click.option('-o', '--output', type=str, default='json')
def hacker_news(post_id, keywords, combinations, output):
    # Your code goes here.
    # Break your problem into smaller chunks using helper functions
    fetch_job_data(post_id, keywords, combinations)
    
    
    exit(0)

def fetch_job_data(post_id, keywords, combinations):
    url = BASE_URL.format(post_id)
    
    data_object = requests.get(url)
    
    data_object.raise_for_status()
    
    root_json_data = data_object.json()
    
    

    
    jobposting = root_json_data['kids']
    
    result_dictionary = {
        'total_jobs' : 0,
        'counts': {},
        'keywords' : {},
        'combinations': {}
    }
    count_dict = result_dictionary['counts']
    
    keywords = keywords.split(',')
    if combinations:
        combo_dict = result_dictionary['combinations']
        for combo in combinations:
            combo_dict[combo] = []
            count_dict[combo] = 0
    
    keyword_dict = result_dictionary['keywords']
    
    
    
    for word in keywords:
        count_dict[word] = 0
        keyword_dict[word] = []

    
    for job in jobposting:
        url = BASE_URL.format(job)
        job_data = requests.get(url)
        job_data_json = job_data.json()
        if not job_data_json.get('text', None):
            continue
        result_dictionary['total_jobs'] += 1
        text = job_data_json['text']
        for word in keywords:
            if word.lower() in text.lower():
                
                count_dict[word] += 1
                keyword_dict[word].append(job_data_json['text'])
        if combinations:
            for combo in combinations:
                words = combo.split('-')
                word_in_text = False
                for word in words:
                    if word.lower() in text.lower():
                        word_in_text = True
                    else:
                        word_in_text = False
                        break
                if word_in_text:
                    combo_dict[combo].append(job)
                    count_dict[combo] += 1
                
                
                 
                    
                    
    
    
    write_file(result_dictionary)



def write_file(result_dictionary):
      with open("jobs.json", "w") as f:
          json.dump(result_dictionary, f)

          

# >>> r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
# >>> r.status_code
# 200
# >>> r.headers['content-type']
# 'application/json; charset=utf8'
# >>> r.encoding
# 'utf-8'
# >>> r.text
# u'{"type":"User"...'
# >>> r.json()
# {u'private_gists': 419, u'total_private_repos': 77, ...}

#https://news.ycombinator.com/item?id=11814828

#[e for e in a_list if all([e % t == 0 for t in a_list_of_terms])]
# ```
if __name__ == '__main__':
    jobs_detector()