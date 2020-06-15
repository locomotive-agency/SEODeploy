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

"""Test Cases for Config Module"""

import pytest

from seodeploy.lib import config
from seodeploy.lib.exceptions import ModuleNotImplemented


@pytest.fixture
def config_class():
    def _config(**kwargs):
        return config.Config(**kwargs)

    return _config


def test_config(config_class):  # noqa
    cfiles = ["tests/files/seotesting_config.yaml"]
    config = config_class(module=None, mdirs=None, cfiles=cfiles)
    assert config.seotesting_name == "SEODeploy-Test"
    assert config.modules == ["contentking", "example_module", "headless"]


def test_config_module(config_class):  # noqa
    cfiles = ["tests/files/seotesting_config.yaml"]
    config = config_class(module="headless", mdirs=None, cfiles=cfiles)
    assert config.headless.pyppeteer_chromium_revision == 769582
    assert config.modules == ["contentking", "example_module", "headless"]


def test_config_wrong_module(config_class):  # noqa
    cfiles = ["tests/files/seotesting_config.yaml"]
    with pytest.raises(ModuleNotImplemented):
        config = config_class(module="doesnt_exist", mdirs=None, cfiles=cfiles)
