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

"""Test Cases for Headless > Init Module"""

from unittest.mock import Mock
import pytest
from pytest_mock import MockFixture

from seodeploy.modules.headless import SEOTestingModule



@pytest.fixture
def mock_run_render(mocker):
    mock = mocker.patch("seodeploy.modules.headless.run_render")
    mock.return_value = {
        "/path1/": {"prod": {'content': {'canonical':'test1'}}, "stage": {'content': {'canonical':'test1'}}, "error": None},
        "/path2/": {"prod": {'content': {'canonical':'test2'}}, "stage": {'content': {'canonical':'test3'}}, "error": None},
        "/path3/": {"prod": None, "stage": None, "error": "error3"},
    }
    return mock



def test_headless_module(mock_run_render):

    headless = SEOTestingModule()
    headless.exclusions = {'content': {'canonical': False}}
    sample_paths = ['/path1/', '/path2/', '/path3/']

    passing, messages, errors = headless.run(sample_paths)

    assert mock_run_render.called
    assert errors == [{'error': 'error3', 'path': '/path3/'}]
    assert messages == [{'type': 'change', 'item': 'content.canonical', 'element': '', 'production': 'test2', 'staging': 'test3', 'module': 'headless', 'path': '/path2/'}]
    assert passing == False
