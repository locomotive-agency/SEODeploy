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


#from lib.logging import get_logger
#from lib.helpers import group_batcher, mp_list_map  # noqa
from exceptions import HeadlessException  # noqa

#_LOG = get_logger(__name__)


def parse_numerical_dict(data, r=2):
    result = {}
    for k,v in data.items():
        if isinstance(v, str):
            v = float(v) if '.' in v else int(v)

        if isinstance(v, float):
            result[k] = round(v, r)
        else:
            result[k] = int(v)

    return result


# Performance Timing Functions
def parse_performance_timing(p_timing):
    ns = p_timing['navigationStart']
    return {k:v-ns if v else 0 for k,v in p_timing.items()}

# Coverage Functions
def parse_coverage_objects(coverage, typ):

    totalUnused = 0
    totalBytes = 0
    results = {}

    for file in coverage:

        (url, ranges, text) = file.values()

        totalLength = 0

        for range in ranges:
            (start, end) = range.values()
            length = end - start
            totalLength = totalLength + length

        total = len(text);
        unused = total - totalLength;

        unusedPc = round(((unused + 1) / (total + 1)) * 100, 2);

        results[url] = {'total': total, 'unused':unused, 'unusedPc':unusedPc}

        totalUnused = totalUnused + unused;
        totalBytes = totalBytes + total;

    return {'results': results, 'totalUnused': totalUnused, 'totalBytes': totalBytes}



def parse_coverage(coverageJS, coverageCSS):

    parsedJSCoverage = parse_coverage_objects(coverageJS, 'JS');
    parsedCSSCoverage = parse_coverage_objects(coverageCSS, 'CSS');

    totalUnused = parsedJSCoverage['totalUnused'] + parsedCSSCoverage['totalUnused']
    totalBytes = parsedJSCoverage['totalBytes'] + parsedCSSCoverage['totalBytes']
    unusedPc = round(((totalUnused  + 1) / (totalBytes + 1)) * 100, 2)

    return {'Summary': {'totalBytes': totalBytes, 'totalUnused': totalUnused, 'unusedPc': unusedPc},
            'CSS': parsedCSSCoverage,
            'JS': parsedJSCoverage
            }
