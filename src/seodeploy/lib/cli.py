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


import json
import click

from seodeploy.lib import SEOTesting
from seodeploy import __version__

from .logging import get_logger
from .exceptions import IncorrectParameters
from .sampling import get_sample_paths
from .config import Config

CONFIG = Config()

_LOG = get_logger(__name__)


# Group all parameter functions....
@click.group()
@click.version_option(version=__version__)
def cli():
    """SEODeploy: Flexible and Modular Python Library for Automating SEO Testing in Deployment Pipelines"""


# Create Samples CLI.
@click.command()
@click.option(
    "--site_id",
    type=str,
    default=None,
    help="If given, the this will sample URLs from your ContentKing site, up to the limit set.",
)
@click.option(
    "--sitemap_url",
    type=str,
    default=None,
    help="If given, the this will sample URLs from the specified sitemap or sitemap index.",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limits the output to this many total paths. Overrides limit set in seotesting_config.yaml.",
)
@click.option(
    "--samples_filename",
    type=str,
    default=None,
    help="Filename for the outputted txt file. Overrides filename set in seotesting_config.yaml.",
)
def sample(site_id, sitemap_url, limit=None, samples_filename=None):
    """Creates sample_paths.txt File."""

    # Error Cheching
    if not site_id and not sitemap_url:
        err = "Either `site_id` or `sitemap_url`are required to run sampling."
        _LOG.error(err)
        raise IncorrectParameters(err)

    # Main function
    if site_id:
        samples = get_sample_paths(
            CONFIG, site_id=site_id, limit=limit, filename=samples_filename
        )
        _LOG.info("Top 5 out of {} sampled Paths for {}".format(len(samples), site_id))
        _LOG.info(json.dumps(samples[:5], indent=4))
    else:
        samples = get_sample_paths(
            CONFIG, sitemap_url=sitemap_url, limit=limit, filename=samples_filename
        )
        _LOG.info(
            "Top 5 out of {} sampled Paths for {}".format(len(samples), sitemap_url)
        )
        _LOG.info(json.dumps(samples[:5], indent=4))

    return 0


# Main Test Function
@click.command()
@click.option(
    "--samples_filename",
    type=str,
    default=None,
    help="Filename for the samples file. Overrides filename set in seotesting_config.yaml.",
)
def execute(samples_filename=None):
    """Difftest Staging and Production URLs."""

    # Set samples_filename.
    samples_filename = samples_filename or CONFIG.SAMPLES_FILENAME

    # Error Cheching
    if not samples_filename:
        raise IncorrectParameters(
            "You must provide either `samples_filename` "
            + "or set `samples_filename` in `seotesting_config.yaml`."
        )

    # Main function
    seotesting = SEOTesting(CONFIG)

    passing = seotesting.execute(samples_filename=samples_filename)

    return 1 if passing else 0


cli.add_command(sample)
cli.add_command(execute)
