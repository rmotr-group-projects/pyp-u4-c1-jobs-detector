import click
import requests
from os import path
import json
import pickle
import xml.etree.ElementTree as ET
import pprint

from jobs_detector import settings
from jobs_detector.exceptions import *

DEFAULT_KEYWORDS = [
    # Put your default keywords here
    "remote", "postgres", "python", "javascript", "react", "pandas"
]


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
    
    keyword_filter_dict = keyword_filter(post_id, keywords)
    
    combo_filter_dict = combo_filter(keyword_filter_dict, post_id, combinations)
    
    output_json(combo_filter_dict)
    
    # for i in range(len(combo_list)):      
    #     filtered_text = filter(job_list, combo_list[i])
    #     return filtered_text
    
    # Filter regimentSize by the lambda function filter
    # filteredRegiments = filter(lessThan2500Filter, regimentSize)
    

def hacker_news_api_call(post_id):
    r = requests.get(settings.BASE_URL.format(post_id))
    return r.json()

def get_jobs(post_id):
    json_result = hacker_news_api_call(post_id)
    kids_list = json_result['kids']
    text = []
    for kid in kids_list:
        result = hacker_news_api_call(kid)
        if result.get('text', None):
            text_results = result['text']
            text.append(text_results)
    return text    

def keyword_filter(post_id, keywords):
    
    job_list = get_jobs(post_id)
    number_of_jobs = len(job_list)
    
    #this will create a dictionary with each keyword and the jobs that contain that keyword
    keyword_list = keywords.split(",")
    keyword_dict = {}
    for word in keyword_list:
        keyword_dict[word] = [job for job in job_list if word.lower() in job.lower()]
        
    #this will create a dictionary of all the keys and the number of jobs 
    count_dict = {}
    for keyword_key in keyword_dict:
        count_dict[keyword_key] = len(keyword_dict[keyword_key])
        
    # this combines all of the parts of info into one large dictionary
    filtered_results = {
        "total_jobs": number_of_jobs,
        "counts": count_dict,
        "keywords": keyword_dict,
        
        }
    return filtered_results

def combo_filter(input_dictionary, post_id, combinations):
    
    job_list = get_jobs(post_id)
    
    
    #this will create a dictionary with each combination and the jobs that contain that combination 
    combo_dict = {}
    if combinations:
        for combo in combinations:
            combo_list = combo.split("-")
            combo_dict[combo] = [job for job in job_list if all(word.lower() in job.lower() for word in combo_list)]
        
    #this will add the combinations and their counts to the count dictionary
    for combo_key in combo_dict:
        input_dictionary['counts'][combo_key] = len(combo_dict[combo_key])
    
    if combinations:    
        input_dictionary['combinations'] = combo_dict
    
    return input_dictionary
    
def output_json(text):
    with open(path.join(settings.BASE_DIR, 'jobs.json'), 'w') as f:
        json.dump(text, f)


if __name__ == '__main__':
    jobs_detector()
