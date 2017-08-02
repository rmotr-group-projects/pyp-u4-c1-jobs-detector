import click
import requests
from os import path
import json
import pickle
import xml.etree.ElementTree as ET

from jobs_detector import settings
from jobs_detector.exceptions import *

RESULT_FORMAT = "{}: {} ({}%)"
DEFAULT_KEYWORDS = [
    'remote',
    'postgres',
    'python',
    'javascript',
    'react',
    'pandas'
]


@click.group()
def jobs_detector():
    pass


@jobs_detector.command()
@click.option('-i', '--post-id', type=str, required=True)
@click.option('-k', '--keywords', type=str, default=','.join(DEFAULT_KEYWORDS))
@click.option('-c', '--combinations', type=str,
              callback=lambda _, __, x: x.split(',') if x else x)
@click.option('-o', '--output', type=str, default='json')
def hacker_news(post_id, keywords, combinations, output):
    keywords_list = keywords.split(',')

    # get all job offers in the Hacker News post
    job_offers = get_job_offers(post_id)

    # count amount of job offers containing each keyword
    search_results = search_for_keywords(job_offers, keywords_list)

    combo_results = None

    if combinations:
        combo_terms = []
        for c in combinations:
            combo_terms.append(tuple(c.split('-')))
        combo_results = search_combinations(job_offers, combo_terms)

    output_results(output.lower(), len(job_offers), search_results, combo_results)

def get_job_offers(post_id):
    """
    Generates a Soup from Hacker News response HTML content, finds all
    job offers and returns them.
    """
    url = settings.BASE_URL.format(post_id)
    response = requests.get(url)
    if not response.status_code == requests.codes.ok:
        raise ValueError('Got unexpected response from Hacker News '
                         'site: {}'.format(response.status_code))
    posts = (requests.get(settings.BASE_URL.format(pid)).json() for pid in response.json()['kids'])
    job_offers = [post['text'] for post in posts if post.get('text', None)]
    return job_offers


def search_for_keywords(job_offers, keywords):
    """
    Returns a dictionary containing all keywords as keys and the counter
    of job offers that include that keyword.
    """
    search_results = {key: [post for post in job_offers
                            if key.lower() in post['text'].lower()]
                      for key in keywords}
    return search_results


def _check_combination(job_offer, combination):
    """
    Returns True if all keywords in the combination are included
    in given job offer text, and False otherwise.
    """
    return all((c.lower() in job_offer['text'].lower() for c in combination))


def search_combinations(job_offers, combos):
    print('search combos')
    search_results = {'-'.join(c): [post for post in job_offers
                          if _check_combination(post, c)]
                      for c in combos}
    print('search complete')
    return search_results

def output_results(output_mode, num_jobs, search_results, combo_results):
    results = {'total_jobs': num_jobs,
               'counts': {kw: len(search_results[kw]) for kw in search_results},
               'keywords': search_results}
    if combo_results:
        results['counts'].update({combo: len(combo_results[combo]) for combo in combo_results})
        results['combinations'] = combo_results

    if output_mode == 'json':
        output_to_json(results)
    elif output_mode == 'xml':
        output_to_xml(results)
    elif output_mode == 'pickle':
        output_to_pickle(results)
    else:
        raise InvalidOutputFormat()

def output_to_json(results):
    output_file = path.join(settings.BASE_DIR, 'jobs.json')
    with open(output_file, 'w') as f:
        json.dump(results, f)

def output_to_xml(results):
    output_file = path.join(settings.BASE_DIR, 'jobs.xml')
    job_search = ET.Element('job_search')
    summary = ET.SubElement(job_search, 'summary')
    ET.SubElement(summary, 'total_jobs').text = str(results['total_jobs'])
    for kw, cnt in results['counts'].items():
        ET.SubElement(summary, 'count', name=str(kw)).text = str(cnt)
    keywords = ET.SubElement(job_search, 'keywords')
    for kw, jobs in results['keywords'].items():
        keyword = ET.SubElement(keywords, 'keyword', name=str(kw))
        for job in jobs:
            ET.SubElement(keyword, 'job').text = str(job)
    if results.get('combinations', None):
        combinations = ET.SubElement(job_search, 'combinations')
        for cmb, jobs in results['combinations'].items():
            combo = ET.SubElement(combinations, 'combination', name=str(cmb))
            for job in jobs:
                ET.SubElement(combo, 'job').text = str(job)
    tree = ET.ElementTree(job_search)
    tree.write(output_file)

def output_to_pickle(results):  
    output_file = path.join(settings.BASE_DIR, 'jobs.pickle')
    with open(output_file, 'wb') as picklefile:
        pickle.dump(results, picklefile)





# def print_results(job_offers, search_results):
#     """
#     Prints keyword matching results to the standar output respecting
#     the expected format.
#     """
#     print("Total job posts: {}".format(len(job_offers)))
#     print("Keywords:")
#     for keyword in search_results.keys():
#         results = search_results[keyword]
#         percentage = int((float(results) / len(job_offers)) * 100)
#         print(RESULT_FORMAT.format(keyword.capitalize(), results, percentage))


# def print_combo(job_offers, combo_results):
#     """
#     Prints keyword combination results to the standar output respecting
#     the expected format.
#     """
#     print("Combinations:")
#     for combo in combo_results.keys():
#         results = combo_results[combo]
#         percentage = int((float(results) / len(job_offers)) * 100)
#         combo_name = "-".join([x.capitalize() for x in combo])
#         print(RESULT_FORMAT.format(combo_name, results, percentage))


if __name__ == '__main__':
    jobs_detector()
