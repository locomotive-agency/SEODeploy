#! /usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2020 JR Oakes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import math
import random


import gzip
import requests
from bs4 import BeautifulSoup

from seodeploy.modules.contentking import SEOTestingModule
from .logging import get_logger
from .helpers import url_to_path




_LOG = get_logger(__name__)


# CALCULATE THE SAMPLE SIZE
def get_sample_size(population_size, confidence_level, confidence_interval):

    Z = 0.0  # noqa
    p = 0.5  # noqa
    e = confidence_interval / 100.0  # noqa
    N = population_size  # noqa
    n_0 = 0.0  # noqa
    n = 0.0  # noqa

    confidence_level_constant = [50, .67], [68, .99], [90, 1.64], [95, 1.96], [99, 2.57]

    # LOOP THROUGH SUPPORTED CONFIDENCE LEVELS AND FIND THE NUM STD
    # DEVIATIONS FOR THAT CONFIDENCE LEVEL
    for i in confidence_level_constant:
        if i[0] == confidence_level:
            Z = i[1]  # noqa

    if Z == 0.0:  # noqa
        return -1

    # CALC SAMPLE SIZE
    n_0 = ((Z ** 2) * p * (1 - p)) / (e ** 2)  # noqa

    # ADJUST SAMPLE SIZE FOR FINITE POPULATION
    n = n_0 / (1 + ((n_0 - 1) / float(N)))  # noqa

    return int(math.ceil(n))  # noqa



def read_sitemap_urls(sitemap_url, limit=None):

    all_urls = []

    headers = {'User-Agent': "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
               'Accept-Encoding': "gzip"}

    try:
        response = requests.get(sitemap_url, headers=headers)
        if response.headers['Content-Type'].lower() == 'application/x-gzip':
            xml = gzip.decompress(response.content)
        else:
            xml = response.content
        soup = BeautifulSoup(xml, "lxml")
        urls = [url.get_text().lower() for url in soup.find_all("loc")]

        while urls:

            url = urls.pop(0)

            if '.xml' in url[-8:]:
                urls.extend(read_sitemap_urls(url))
                continue

            all_urls.append(url)

            if limit and len(all_urls) >= limit:
                break


    except Exception as e:  # noqa
        _LOG.error('Read Sitemap Error: ', str(e))

    return all_urls



def get_sample_paths(config, site_id=None, sitemap_url=None, limit=None, filename=None):

    limit = limit or config.URL_LIMIT
    filename = filename or config.SAMPLES_FILENAME

    if os.path.isfile(filename):
        _LOG.info('Reloading Existing Sample File: ' + filename)
        with open(filename) as file:
            content = file.readlines()

        sample_paths = [x.strip() for x in content]
        return sample_paths

    if site_id:
        content_king = SEOTestingModule()
        all_urls = content_king.get_samples(site_id, limit)

    elif sitemap_url:
        all_urls = read_sitemap_urls(sitemap_url, limit)

    else:
        _LOG.error('No file found and site_id not specified. Returning an empty list.')
        return []

    count_urls = len(all_urls)
    sample_size = get_sample_size(count_urls, config.CONFIDENCE_LEVEL, config.CONFIDENCE_INTERVAL)
    random_sample = random.sample(range(count_urls), sample_size)

    sample_urls = [v for i, v in enumerate(all_urls) if i in random_sample]  # noqa
    sample_paths = [url_to_path(u) for u in sample_urls]

    _LOG.info('Total URLs: {} Samples: {}'.format(count_urls, len(sample_paths)))

    with open(filename, 'w') as file:
        file.writelines("{}\n".format(path) for path in sample_paths)
        _LOG.info('Saved Sample File: ' + filename)

    return sample_paths
