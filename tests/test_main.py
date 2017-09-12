# -*- coding: utf-8 -*-
from __future__ import print_function

import re
import os
import unittest
import traceback
import sys
import json
import pickle

import six

import xml.etree.ElementTree as ET

import responses
from click.testing import CliRunner

from jobs_detector import settings
from jobs_detector.main import jobs_detector

from . import fixtures

def handle_errors(result):
    if not isinstance(result.exc_info[1], SystemExit) or\
        result.exc_info[1].code != 0:
        excep_type, orig_excep, tb = result.exc_info
        six.reraise(excep_type, orig_excep, tb)

class HackerNewsTestCase(unittest.TestCase):

    def setUp(self):
        self.post_id = '11814828'
        fixtures.load_fixtures()

    @responses.activate
    def test_hacker_news_default_keywords(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news', '-i', self.post_id]
        )

       handle_errors(result)

        with open(os.path.join(settings.BASE_DIR, 'jobs.json')) as f:
            data = json.load(f)

        expected_total = 800
        expected_counts = {'remote': 179,
                           'postgres': 87,
                           'python': 164,
                           'javascript': 131,
                           'react': 143,
                           'pandas': 6}

        self.assertEqual(data['total_jobs'], expected_total)
        self.assertEqual(data['counts'], expected_counts)

        javascript_job = "QA Lead &amp; Core Engineer | Replicated | Los Angeles | $70k - $80k, $130k - $150k both with equity |"
        self.assertTrue(any((job.startswith(javascript_job) for job in data['keywords']['javascript'])))
        

    @responses.activate
    def test_hacker_news_custom_keywords(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news',
             '-i', self.post_id,
             '-k', 'python,django']
        )

        handle_errors(result)

        with open(os.path.join(settings.BASE_DIR, 'jobs.json')) as f:
            data = json.load(f)

        expected_total = 800
        expected_counts = {'python': 164,
                           'django': 39}

        self.assertEqual(data['total_jobs'], expected_total)
        self.assertEqual(data['counts'], expected_counts)

    @responses.activate
    def test_hacker_news_combinations(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news',
             '-i', self.post_id,
             '-c', 'python-remote,python-django,django-remote']
        )

        handle_errors(result)

        with open(os.path.join(settings.BASE_DIR, 'jobs.json')) as f:
            data = json.load(f)

        expected_total = 800
        expected_counts = {'remote': 179,
                           'postgres': 87,
                           'python': 164,
                           'javascript': 131,
                           'react': 143,
                           'pandas': 6,
                           'python-remote': 33,
                           'django-remote': 8,
                           'python-django': 38}

        self.assertEqual(data['total_jobs'], expected_total)
        self.assertEqual(data['counts'], expected_counts)

    @responses.activate
    def test_hacker_news_keywords_and_combinations(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news',
             '-i', self.post_id,
             '-k', 'python,django',
             '-c', 'python-remote,python-django,django-remote']
        )

        handle_errors(result)

        with open(os.path.join(settings.BASE_DIR, 'jobs.json')) as f:
            data = json.load(f)

        expected_total = 800
        expected_counts = {'python': 164,
                           'django': 39,
                           'python-remote': 33,
                           'django-remote': 8,
                           'python-django': 38}

        self.assertEqual(data['total_jobs'], expected_total)
        self.assertEqual(data['counts'], expected_counts)

"""
    @responses.activate
    def test_hacker_news_pickle(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news', '-i', self.post_id, '-o', 'pickle']
        )

        handle_errors(result)

        with open(os.path.join(settings.BASE_DIR, 'jobs.pickle'), 'rb') as f:
            data = pickle.load(f)

        expected_total = 800
        expected_counts = {'remote': 179,
                           'postgres': 87,
                           'python': 164,
                           'javascript': 131,
                           'react': 143,
                           'pandas': 6}

        self.assertEqual(data['total_jobs'], expected_total)
        self.assertEqual(data['counts'], expected_counts)

    @responses.activate
    def test_hacker_news_xml(self):
        runner = CliRunner()
        result = runner.invoke(
            jobs_detector,
            ['hacker_news', '-i', self.post_id, '-o', 'xml']
        )

        handle_errors(result)

        xmlfile = os.path.join(settings.BASE_DIR, 'jobs.xml')
        tree = ET.parse(xmlfile)
        job_search = tree.getroot()

        with open(os.path.join(settings.BASE_DIR, 'jobs.pickle'), 'rb') as f:
            data = pickle.load(f)

        expected_total = 800
        expected_counts = {'remote': 179,
                           'postgres': 87,
                           'python': 164,
                           'javascript': 131,
                           'react': 143,
                           'pandas': 6}
        summary = job_search.find('summary')

        self.assertEqual(int(summary.find('total_jobs').text), expected_total)
        for cnt in summary.findall('count'):
            self.assertEqual(int(cnt.text), expected_counts[cnt.get('name')])
"""
