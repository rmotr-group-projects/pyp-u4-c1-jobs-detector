import click
import requests
from os import path
import json
import pickle
import xml.etree.ElementTree as ET

from jobs_detector import settings
from jobs_detector.exceptions import *

BASE_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'

DEFAULT_KEYWORDS = ['remote', 'postgres', 'python', 'javascript', 'react', 'pandas']

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

    def get_postings_list(post_id):#, keywords, combinations, output):
        '''get a list of postings from the main page'''
        r = requests.get(BASE_URL.format(post_id))
        postings_list = r.json()['kids']
        return postings_list

    def extract_contents(postings_list_in):
        '''check the individual postings'''
        for item in postings_list_in:
            r = requests.get(BASE_URL.format(item))
            posting = r.json()
            yield posting

    def parse_keywords(keywords_in):
        '''keywords come in as single string, separated by commas'''
        if ',' in keywords_in:
            return keywords_in.split(',')
        else:
            return [keywords_in]

    def parse_combos(combos_in):
        '''example of combos_in from test ['python-remote', 'python-django', 'django-remote']'''
        combos_out = [(combo, combo.split('-')) for combo in combos_in]
        return combos_out# (combos_in, combos_in.split('-'))#

    def cycle_through_posts(postings_in,keywords_in, combos_in=None):
        running_total = 0
        if keywords_in:
            parsed_keywords = parse_keywords(keywords_in)
            results_dict = {k:[] for k in parsed_keywords}
        else:
            parsed_keywords = []
            results_dict = {}
        if combos_in: 
            parsed_combos = parse_combos(combos_in)
            combo_dict = {c:[] for c in combos_in} 
        else:
            parsed_combos = None
            combo_dict = None
        while True:
            try:
                posting = next(postings_in)
                text = posting.get('text')
                if not text:
                    pass
                else:
                    running_total += 1
                    results_dict = check_keywords(text, parsed_keywords, results_dict)
                    combo_dict = check_combos(text, parsed_combos, combo_dict)
            except StopIteration:
                return running_total, results_dict, combo_dict
    
    def check_keywords(text_in, keywords_in, results_dict):
        for word in keywords_in:
            if word in text_in.lower():
                results_dict[word].append(text_in)
        return results_dict
    
    def check_combos(text_in, parsed_combos_in, combo_dict):
        if not combo_dict:
            return None
        else:
            for combo in parsed_combos_in:
                if all(term in text_in.lower() for term in combo[1]):
                    combo_dict[combo[0]].append(text_in)
            return combo_dict

    def parse_results(running_total, results_dict, combo_dict):
        results = {}
        results['total_jobs'] = running_total
        if results_dict:
            res_count = {k:len(v) for k, v in results_dict.items() if len(v) > 0}
            results['keywords'] = results_dict
        else:
            res_count = {}
        if combo_dict:
            comb_count = {k:len(v) for k, v in combo_dict.items() if len(v) > 0}
            results['combinations'] = combo_dict
        else:
            comb_count = {}
        total_counts = dict(res_count, **comb_count)
        results['counts'] = total_counts
        return results

    postings_list = get_postings_list(post_id)
    postings = extract_contents(postings_list)
    running_total, keyword_res, comb_res = cycle_through_posts(postings, keywords, combinations)
    results = parse_results(running_total, keyword_res, comb_res)

    with open('jobs.json', 'w') as outfile:  
        json.dump(results, outfile)

if __name__ == '__main__':
    jobs_detector()
