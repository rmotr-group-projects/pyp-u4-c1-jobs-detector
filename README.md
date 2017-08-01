# [pyp-w3] Jobs Detector

Today we will develop a command line tool which aims to parse certain websites looking for job statistics based on given keywords. In this project we will implement a parser for the HackerNews blog, which includes a monthly report of "Who is hiring?". Example: https://news.ycombinator.com/item?id=11814828

We are going to access this data through HackerNews' publicly available API which has documentation available at: https://github.com/HackerNews/API We will be accessing the the api using the Requests library (http://docs.python-requests.org/en/master/)

Requests makes it **very** easy to access APIs:
```
>>> r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
>>> r.status_code
200
>>> r.headers['content-type']
'application/json; charset=utf8'
>>> r.encoding
'utf-8'
>>> r.text
u'{"type":"User"...'
>>> r.json()
{u'private_gists': 419, u'total_private_repos': 77, ...}
```


## Command usage

The command line tool must be accessible by calling `jobs_detector` command. A `hacker_news` subcommand must be also available as part of this implementation.

To see the whole list of optional and mandatory parameters, you can execute the command using the `--help` flag.

```bash
$ jobs_detector hacker_news --help
Options:
  -i, --post-id TEXT       [required]
  -k, --keywords TEXT
  -c, --combinations TEXT
  -o, --output TEXT
  --help                   Show this message and exit.
```

### Default arguments

To request jobs statistics using a default set of keywords, just call the `hacker_news` subcommand providing a valid HN post id (see the last part of the sample URL above), like this:

```bash
$ jobs_detector/jobs_detector hacker_news -i 11814828
```
This will output a jobs.json to our root project directory with the following format:
```
{
"total_jobs": 123,
"counts": {"remote": 10,
		   "postgres": 6,
		   "python": 20,
		   "javascript": 14,
		   "react": 15,
		   "pandas": 3},
"keywords": {"remote": [a list containing the text of each matching posting],
			 ...
			}
}
```

### Keywords filtering

For statistics about a sub set of the default keywords, or even custom keywords out of the default set you can specify the `-k` or `--keywords` options, as a comma separated list of values.

```bash
$ jobs_detector hacker_news -i 11814828 -k python,django,ruby
```
```
{
"total_jobs": 123,
"counts": {"python": 20,
		   "django": 14,
		   "ruby": 15},
"keywords": {"python": [a list containing the text of each matching posting],
			 ...
			}
}
```

### Combination stats

It's also possible to request statistics of certain combination of keywords. For example, how many offers are asking for "remote", "python", and "flask" at the same time?. To do that, use the `-c` or `-combinations` option.

```bash
$ jobs_detector hacker_news -i 11814828 -c remote-python-flask,remote-django
```
```
{
"total_jobs": 123,
"counts": {"remote": 10,
		   "postgres": 6,
		   "python": 20,
		   "javascript": 14,
		   "react": 15,
		   "pandas": 3,
		   "remote-python-flask": 6,
		   "remote-django": 4},
"keywords": {"remote": [a list containing the text of each matching posting],
			 ...
			}
"combinations": {"remote-python-flask": [list of postings],
				 ...
				}
}
```

If you wish to extend the functionality of this we have included commented out tests for output in xml or pickle by using the command argument `-o xml` or `-o pickle` such as:
```bash
$ jobs_detector hacker_news -i 11814828 -c remote-python-flask,remote-django -o xml
```
Relevant Python documentation for xml and pickle:

 - https://docs.python.org/3/library/xml.etree.elementtree.html
 - https://docs.python.org/3/library/pickle.html
 - [Using Pickle to Save Objects in Python](https://www.thoughtco.com/using-pickle-to-save-objects-2813661)

## Your command available in pypi

Finally, to wrap up this group work, you must make your command tool available in pypi (Python Package Index). Any person out there must be able to use the `pip` command and install a local version of your project. To do this, we will follow some naming conventions so we don't have conflicts between each other. This is the naming convention you must follow for your package: `rmotr-bX-cY-gZ-jobs-detector`, where `X`, `Y` and `Z` are the batch number, course number and group number respectively.

Anyone should be able to install the package by executing, for example: `pip install rmotr-b6-c1-g3-jobs-detector`.

Here you have a very detailed guide about how to upload things to pypi: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
