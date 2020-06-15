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

"""Test Cases for ContentKing > Init Module"""

from unittest.mock import Mock
import pytest
import json
from pytest_mock import MockFixture

from seodeploy.modules.contentking import SEOTestingModule
from seodeploy.modules.contentking.exceptions import ContentSamplingError


@pytest.fixture
def mock_run_contentking(mocker):
    mock = mocker.patch("seodeploy.modules.contentking.run_contentking")
    mock.return_value = {
        "/path1/": {
            "prod": {"content": {"canonical": "test1"}},
            "stage": {"content": {"canonical": "test1"}},
            "error": None,
        },
        "/path2/": {
            "prod": {"content": {"canonical": "test2"}},
            "stage": {"content": {"canonical": "test3"}},
            "error": None,
        },
        "/path3/": {"prod": None, "stage": None, "error": "error3"},
    }
    return mock


@pytest.fixture
def mock_load_report(mocker):
    mock = mocker.patch("seodeploy.modules.contentking.load_report")
    with open("tests/files/sample_contentking_pages.json", "r") as rf:
        data = json.load(rf)
    mock.return_value = data
    return mock


def test_contentking_module(mock_run_contentking):

    contentking = SEOTestingModule()
    contentking.exclusions = {"content": {"canonical": False}}
    sample_paths = ["/path1/", "/path2/", "/path3/"]

    messages, errors = contentking.run(sample_paths)

    assert mock_run_contentking.called
    assert errors == [{"error": "error3", "path": "/path3/"}]
    assert messages == [
        {
            "type": "change",
            "item": "content.canonical",
            "element": "",
            "production": "test2",
            "staging": "test3",
            "module": "contentking",
            "path": "/path2/",
        }
    ]


def test_contentking_get_pages(mock_load_report):

    contentking = SEOTestingModule()

    site_id = "5-5671785"
    limit = 2
    all_urls = contentking.get_samples(site_id, limit)

    assert mock_load_report.called
    assert len(all_urls) == 2

    limit = None
    all_urls = contentking.get_samples(site_id, limit)
    assert len(all_urls) == 150


def test_contentking_get_pages_bad_report(mock_load_report):

    contentking = SEOTestingModule()
    site_id = "5-5671785"
    limit = 5

    mock_load_report.return_value = []

    # no Results
    with pytest.raises(ContentSamplingError):
        all_urls = contentking.get_samples(site_id, limit)

    mock_load_report.return_value = ["None", None, False]

    # Bad results
    with pytest.raises(ContentSamplingError):
        all_urls = contentking.get_samples(site_id, limit)
