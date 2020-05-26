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
import sys
import importlib

from dictdiffer import diff

from .config import Config
from .logging import get_logger
from .exceptions import StrategyNotImplemented


_LOG = get_logger(__name__)


"""
Format that Class is looking for for all comparision data.

[
    {'name': <string>,
     'item1': <string>, <dict>, <list>,
     'item2': <string>, <dict>, <list>,
     'compare_strategy':<string>,
     'threshold': <float> or None
     },
     {},
     ...
]
"""

class StrategyBase():
    """Base strategy module. Strategy modules run comparative analysis on module content
    based on selected strategy.

    """

    def __init__(self, config=None, exclusions=None):
        self.messages = None
        self.exclusions = exclusions
        self.config = config or Config()

    # Strategies:
    def compare_list_of_dicts(self, d1, d2):
        return [v for i,v in enumerate(d2) if v not in d1]


    def compare_flat_dicts(self, d1, d2, tolerance=None):
        """Expects data (d1, d2) in the format:
            {
            'key1', 'value1',
            'key2': 'value2',
            'key3': 2,
            'key4': 2.12,
            ...
            }

            tolerance: <float> is % difference for numeric values calculated as
            differences.


        """
        return diff(d1, d2, tolerance=tolerance)


    @staticmethod
    def format_change(diffs):

        results = []

        for diff in diffs:
            ctype, element, details = diff

            if ctype == "change":
                results.append({'type': ctype, 'item': element, 'before': details[0], 'after': details[1]})
            else:
                for item in details:
                    results.append({'type': ctype, 'item': item[0], 'content': item[1]})

        return results


    @staticmethod
    def l2d(l1, l2, key_attr, content_attr):
        """Turns a list of dicts into a dict based on given key attribute and content attribute.
            parameters:
                l1: <list> first list of dicts.
                l2: <list> second list of dicts.
                key_attr: <str> dict key to be used as key for new dict.
                content_attr: <str> or <list> dict key(s) to be used as value for new dict.
        """
        if isinstance(content_attr, str):
            d1 = {i[key_attr]:i[content_attr] for i in l1 if i[key_attr] and len(i[key_attr])}
            d2 = {i[key_attr]:i[content_attr] for i in l2 if i[key_attr] and len(i[key_attr])}
        elif isinstance(content_attr, list):
            d1 = {i[key_attr]:{i[v] for v in content_attr} for i in l1 if i[key_attr] and len(i[key_attr])}
            d2 = {i[key_attr]:{i[v] for v in content_attr} for i in l2 if i[key_attr] and len(i[key_attr])}
        else:
            raise NotImplementedError("`content_attr` can only be of type `str` or `list`")


    return d1,d2


    def compare_data(self, data):
        raise NotImplementedError

    def run(self, samples):
        raise NotImplementedError







class
