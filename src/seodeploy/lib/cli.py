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

"""SEODeploy: CLI."""

import json
import click

from seodeploy.lib import SEOTesting
from seodeploy import __version__

from seodeploy.lib.logging import get_logger
from seodeploy.lib.exceptions import IncorrectParameters
from seodeploy.lib.sampling import get_sample_paths
from seodeploy.lib.config import Config


_LOG = get_logger(__name__)


# Group all parameter functions....
@click.group()
@click.version_option(version=__version__)
def cli():
    """SEODeploy: Flexible and Modular Python Library for Automating SEO Testing in Deployment Pipelines."""


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
    help="Limits the output to this many total paths. Overrides limit set in seodeploy_config.yaml.",
)
@click.option(
    "--samples_filename",
    type=str,
    default=None,
    help="Filename for the outputted txt file. Overrides filename set in seodeploy_config.yaml.",
)
@click.option(
    "--config_file",
    type=str,
    default=None,
    help="Filename for the config file. Overrides the default: seodeploy_config.yaml. Falls back to default if not found.",
)
def sample(site_id, sitemap_url, limit=None, samples_filename=None, config_file=None):
    """Create sample_paths.txt File."""

    # Error Cheching
    if not site_id and not sitemap_url:
        err = "Either `site_id` or `sitemap_url`are required to run sampling."
        raise IncorrectParameters(err)

    config = Config(cfiles=[config_file]) if config_file else Config()

    # Main function
    if site_id:
        samples = get_sample_paths(
            config, site_id=site_id, limit=limit, filename=samples_filename
        )
        _LOG.info("Top 5 out of {} sampled Paths for {}".format(len(samples), site_id))
        _LOG.info(json.dumps(samples[:5], indent=4))
    else:
        samples = get_sample_paths(
            config, sitemap_url=sitemap_url, limit=limit, filename=samples_filename
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
    help="Filename for the samples file. Overrides filename set in seodeploy_config.yaml.",
)
@click.option(
    "--config_file",
    type=str,
    default=None,
    help="Filename for the config file. Overrides the default: seodeploy_config.yaml. Falls back to default if not found.",
)
def execute(samples_filename=None, config_file=None):
    """Difftest Staging and Production URLs."""

    # Maybe set config file.
    config = Config(cfiles=[config_file]) if config_file else Config()

    # Set samples_filename.
    samples_filename = samples_filename or config.SAMPLES_FILENAME

    # Error Cheching
    if not samples_filename:
        raise IncorrectParameters(
            "You must provide either `samples_filename` "
            + "or set `samples_filename` in `seodeploy_config.yaml`."
        )

    sample_paths = get_sample_paths(config, filename=samples_filename)

    # Main function
    seotesting = SEOTesting(config=config)

    passing = seotesting.execute(sample_paths=sample_paths)

    return 1 if passing else 0


cli.add_command(sample)
cli.add_command(execute)
