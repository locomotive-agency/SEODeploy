
import math
import random
from urllib.parse import urlparse, urlsplit

from lib.log_helper import get_logger
import lib.contentking as ck

import config

_LOG = get_logger(__name__)



# CALCULATE THE SAMPLE SIZE
# From: https://github.com/Marie-de-Leseleuc/Python-Code/blob/557805e1d9cbb72c62920b81fe36375a45199f99/2-%20Sample%20size/sample_size_calculator.py
def get_sample_size(population_size, confidence_level, confidence_interval):
    Z = 0.0
    p = 0.5
    e = confidence_interval/100.0
    N = population_size
    n_0 = 0.0
    n = 0.0

    confidence_level_constant = [50,.67], [68,.99], [90,1.64], [95,1.96], [99,2.57]


    # LOOP THROUGH SUPPORTED CONFIDENCE LEVELS AND FIND THE NUM STD
    # DEVIATIONS FOR THAT CONFIDENCE LEVEL
    for i in confidence_level_constant:
        if i[0] == confidence_level:
            Z = i[1]

    if Z == 0.0:
        return -1

    # CALC SAMPLE SIZE
    n_0 = ((Z**2) * p * (1-p)) / (e**2)

    # ADJUST SAMPLE SIZE FOR FINITE POPULATION
    n = n_0 / (1 + ((n_0 - 1) / float(N)) )

    return int(math.ceil(n)) # THE SAMPLE SIZE


def url_to_path(url):
    p = urlsplit(url)
    return  p.path if not p.query else p.path + "?" + p.query



def get_sample_paths(site_id, limit=None, filename=None):

    limit    = limit or config.URL_LIMIT
    filename = filename or config.SAMPLES_FILENAME

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


    count_urls    = len(all_urls)
    sample_size   = get_sample_size(count_urls, config.CONFIDENCE_LEVEL, config.CONFIDENCE_INTERVAL)
    random_sample = [ i for i in random.sample( range(count_urls), sample_size ) ]

    sample_urls   = [v for i, v in enumerate(all_urls) if i in random_sample]

    sample_paths = [url_to_path(u) for u in sample_urls]

    _LOG.info('Total URLs: {} Samples: {}'.format(count_urls, len(sample_paths)))

    with open(filename, 'w') as file:
        file.writelines("{}\n".format(path) for path in sample_paths)


    return sample_paths
