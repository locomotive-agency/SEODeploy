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
     'tolerance': <float> or None
     },
     {},
     ...
]
"""

class CompareBase():
    """Base strategy module. Strategy modules run comparative analysis on module content
    based on selected strategy.

    """

    def __init__(self, config=None, exclusions=None):
        self.messages = []
        self.exclusions = exclusions
        self.differences = {}
        self.config = config or Config()


    def compare(self, path, ctype, d1, d2, exclusions=None):

        self.exclusions = exclusions or self.exclusions



    def add_message(self, path, typ, diffs):
        self.messages.extend({'path': path, 'url': , 'type', typ, 'differences': diffs})

    def get_messages(self):
        self._build_messages()
        return self.messages


    def _build_messages(self):


    @staticmethod
    def compare_lists_of_objects(l1, l2, key_attr, content_attr, tolerance=None):

        # Changes list to dict based on given key_attr and content_attr values.
        d1, d2 = self.l2d(l1, l2, key_attr, content_attr)

        return self.compare_objects(d1, d2, tolerance=tolerance)


    @staticmethod
    def compare_objects(d1, d2, tolerance=None):

        tolerance = tolerance or 0

        if isinstance(d1, list) and isinstance(d2, list):
            otype = 'set'
            d1, d2 = set(d1), set(d2)
        elif isinstance(d1, set) and isinstance(d1, set):
            otype = 'set'
            pass
        elif isinstance(d1, dict) and isinstance(d1, dict):
            otype = 'dict'
        else:
            raise AttributeError('Unsupported object types provided.  Supports `list`, `set`, or `dict`')


        diffs = diff(d1, d2, tolerance=tolerance)

        return self.format_diffs(diffs, otype)


    @staticmethod
    def format_diffs(diffs, otype):

        results = []

        for diff in diffs:
            ctype, element, details = diff

            if ctype == "change":
                results.append({'type': ctype, 'item': "{}.{}".format(*(element)), 'before': details[0], 'after': details[1]})
            else:
                for detail in details:

                    content = detail[1]

                    if otype == 'dict' and not element:
                        item = detail[0]
                        content = detail[1][0]
                    elif otype == 'dict':
                        item = "{}.{}".format(element, detail[0])
                        content = detail[1]
                    else:
                        item = ''.join(detail[1])
                        content = None

                    results.append({'type': ctype, 'item': item, 'content': content})

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
        d1, d2 = {}, {}

        def adder(k, c, o):
            if k in o:
                o[k] += [c]
            else:
                o[k] = [c]

        if isinstance(content_attr, str):
            _ = [adder(i[key_attr], i[content_attr], d1) for i in l1 if key_attr in i and len(i[key_attr])]
            _ = [adder(i[key_attr], i[content_attr], d2) for i in l2 if key_attr in i and len(i[key_attr])]
        elif isinstance(content_attr, list):
            _ = [adder(i[key_attr], {i[v] for v in content_attr}, d1) for i in l1 if i[key_attr] and len(i[key_attr])]
            _ = [adder(i[key_attr], {i[v] for v in content_attr}, d2) for i in l2 if i[key_attr] and len(i[key_attr])]
        else:
            raise NotImplementedError("`content_attr` can only be of type `str` or `list`")


        return d1,d2


    def compare_data(self, data):
        raise NotImplementedError
