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
from urllib.parse import urlparse, urlsplit

from .lib.log_helper import get_logger
import .lib.contentking as ck

import config

_LOG = get_logger(__name__)


# CALCULATE THE SAMPLE SIZE
def get_sample_size(population_size, confidence_level, confidence_interval):

    Z = 0.0
    p = 0.5
    e = confidence_interval / 100.0
    N = population_size
    n_0 = 0.0
    n = 0.0

    confidence_level_constant = [50, .67], [68, .99], [90, 1.64], [95, 1.96], [99, 2.57]

    # LOOP THROUGH SUPPORTED CONFIDENCE LEVELS AND FIND THE NUM STD
    # DEVIATIONS FOR THAT CONFIDENCE LEVEL
    for i in confidence_level_constant:
        if i[0] == confidence_level:
            Z = i[1]

    if Z == 0.0:
        return -1

    # CALC SAMPLE SIZE
    n_0 = ((Z ** 2) * p * (1 - p)) / (e ** 2)

    # ADJUST SAMPLE SIZE FOR FINITE POPULATION
    n = n_0 / (1 + ((n_0 - 1) / float(N)))

    return int(math.ceil(n))  # THE SAMPLE SIZE


def url_to_path(url):
    p = urlsplit(url)
    return p.path if not p.query else p.path + "?" + p.query


def get_sample_paths(site_id=None, limit=None, filename=None):

    limit = limit or config.URL_LIMIT
    filename = filename or config.SAMPLES_FILENAME

    if os.path.isfile(filename):
        _LOG.INFO('Reloading Existing: ' + filename)
        with open(filename) as f:
            content = f.readlines()

        sample_paths = [x.strip() for x in content]
        return sample_paths

    elif site_id:

        report = 'pages'
        pages = ck.load_report(report, id=site_id, per_page=config.PER_PAGE)

        all_urls = []
        for page in pages:

            if page:
                urls = [url['url'] for url in page if url['is_indexable']]
                all_urls.extend(urls)
            else:
                break

            if limit and len(all_urls) >= limit:
                all_urls = all_urls[:limit]
                break

        count_urls = len(all_urls)
        sample_size = get_sample_size(count_urls, config.CONFIDENCE_LEVEL, config.CONFIDENCE_INTERVAL)
        random_sample = [i for i in random.sample(range(count_urls), sample_size)]

        sample_urls = [v for i, v in enumerate(all_urls) if i in random_sample]
        sample_paths = [url_to_path(u) for u in sample_urls]

        _LOG.INFO('Total URLs: {} Samples: {}'.format(count_urls, len(sample_paths)))

        with open(filename, 'w') as file:
            file.writelines("{}\n".format(path) for path in sample_paths)

        return sample_paths

    else:

        _LOG.INFO('No file found and site_id not specified. Returning an empty list.')
        return []
