import click
import requests
from os import path
import json
import pickle
import xml.etree.ElementTree as ET

from jobs_detector import settings
from jobs_detector.exceptions import *

DEFAULT_KEYWORDS = [
    # Put your default keywords here
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
    pass


if __name__ == '__main__':
    jobs_detector()
