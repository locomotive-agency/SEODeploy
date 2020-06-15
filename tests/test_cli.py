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

"""Test Cases for CLI Module"""

import pytest

from click.testing import CliRunner

from seodeploy.lib.cli import cli, CONFIG
from seodeploy.lib.cli import IncorrectParameters


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture
def mock_get_sample_paths(mocker):
    mock = mocker.patch("seodeploy.lib.cli.get_sample_paths")
    mock.return_value = ["/path1/", "/path2/", "/path3/"]
    return mock


class SEOTest:
    def __init__(self, config):
        self.config = config

    def execute(sample_paths=None):
        if sample_paths:
            return 0
        else:
            return 1


@pytest.fixture
def mock_seotesting(mocker):
    mock = mocker.patch("seodeploy.lib.cli.SEOTesting")
    mock.return_value = SEOTest
    return mock


def test_sample(runner, mock_get_sample_paths):

    with pytest.raises(IncorrectParameters):
        result = runner.invoke(cli, ["sample"], catch_exceptions=False)

    result = runner.invoke(cli, ["sample", "--site_id", "5-111111"])
    assert mock_get_sample_paths.called
    assert result.exit_code == 0

    result = runner.invoke(
        cli, ["sample", "--site_id", "5-111111", "--samples_filename", "filename.txt"]
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli, ["sample", "--sitemap_url", "https://domain.com/sitemap_index.xml"]
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "sample",
            "--sitemap_url",
            "https://domain.com/sitemap_index.xml",
            "--limit",
            "10",
        ],
    )
    assert result.exit_code == 0


def test_execute(runner, mock_get_sample_paths, mock_seotesting):

    with pytest.raises(IncorrectParameters):
        CONFIG.SAMPLES_FILENAME = None
        result = runner.invoke(cli, ["execute"], catch_exceptions=False)

    result = runner.invoke(cli, ["execute", "--samples_filename", "samples.txt"])
    assert mock_get_sample_paths.called
    assert mock_seotesting.called
    assert result.exit_code == 0

    mock_get_sample_paths.return_value = None
    result = runner.invoke(cli, ["sample", "--samples_filename", "samples.txt"])
    assert mock_get_sample_paths.called
    assert mock_seotesting.called
    assert result.exit_code == 1
