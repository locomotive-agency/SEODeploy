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

from datetime import datetime

import json
import click
import pytz

import lib.contentking as ck
import lib.sampling as sp
from lib.exceptions import ContentKingMissing, IncorrectParameters
from lib.log_helper import get_logger

import lib.config import Config

config = Config()

_LOG = get_logger(__name__)


# Group all parameter functions....
@click.group()
def cli():
    pass


# Create Samples CLI.
@click.command()
@click.option('--site_id', type=str, default=None, help='ID of Content King Website.')
@click.option('--site_name', type=str, default=None, help='Name of Content King Website.')
@click.option('--limit', type=int, default=None, help='Limits the output to this many total paths. Overrides limit set in config.py.')
@click.option('--filename', type=str, default=None, help='Filename for the outputted txt file. Overrides filename set in config.py.')
@click.argument('sample')
def create_samples(site_id, site_name, limit=None, filename=None):

    """Creates a file of sample paths to use in testing.

    Parameters
    ----------
    site_id : str
        The ID of the project in Content King (Eg. 4-17147226)
    site_name : str
        The name of the project in Content King.
    limit: int
        Limits the output to this many total paths. Overrides limit set in config.py.
    filename: str
        Filename for the outputted txt file. Overrides filename set in config.py.
    """

    # Error Cheching
    if not site_id and not site_name:
        if config.PROD_SITE_ID:
            _LOG.WARNING('Using `PROD_SITE_ID` from config.py file.')
            site_id = config.PROD_SITE_ID
        else:
            raise IncorrectParameters('You must provide either `site_id` or `site_name` options for sample argument. Or PROD_SITE_ID must be specified in config.py')

    if site_id and site_name:
        _LOG.WARNING('Using `site_id`.  Both `site_id` and `site_name` were given.')

    # Main function
    if site_id:
        samples = sp.get_sample_paths(site_id=site_id, limit=limit, filename=filename)
        _LOG.INFO('Top 5 sampled Paths for {}'.format(site_id))
        _LOG.INFO(json.dumps(samples[:5], indent=4))
    elif site_name:
        sites = [s for s in ck.load_report('websites') if site_name in s['name']]
        if sites:
            site_id = sites['id']
            samples = sp.get_sample_paths(site_id=site_id, limit=limit, filename=filename)
            _LOG.INFO('Top 5 sampled Paths for {}'.format(site_name))
            _LOG.INFO(json.dumps(samples[:5], indent=4))
        else:
            raise ContentKingMissing('No site with matching name: {}'.format(site_name))

    else:
        raise Exception('Could not create samples due to an unknown error.')

    return True


# Main Test Function
@click.command()
@click.option('--filename', type=str, default=None, help="Name of Content King Website.")
@click.argument('difftest')
def run_difftest(filename=None):

    """Runs a difftest of staging vs production based on `config.py` settings and sample URLs.

    Parameters
    ----------
    filename: str
        Filename for the outputted txt file. Overrides filename set in config.py.
    """

    # Configure Timezone
    time_zone = pytz.timezone(config.TIMEZONE)

    # Set filename.
    filename = filename or config.SAMPLES_FILENAME

    # Error Cheching
    if not filename:
        raise IncorrectParameters('You must provide either `filename` or set `SAMPLES_FILENAME` in `config.py`.')

    # Main function

    # By passing no site_id parameters, it will expect the file to exist
    sample_paths = sp.get_sample_paths(filename=filename)

    start_time = datetime.now().astimezone(time_zone).isoformat(timespec='seconds')

    # Runs pings across both staging and production
    ck.run_path_pings(sample_paths)  # TODO: Do something with result.

    # Monitor results.
    ck.run_check_results(sample_paths, start_time, time_zone)   # TODO: Do something with result.
