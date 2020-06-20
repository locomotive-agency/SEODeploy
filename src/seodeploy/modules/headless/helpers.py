#!/usr/bin/env python
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

from urllib.parse import quote_plus

from seodeploy.lib.helpers import dot_get

# Default User Agent for requests.  If not set in YAML.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"  # pylint: disable=line-too-long


# Various extractions to run on Chrome.
"""
EXTRACTIONS = {
    "title": "() => [...document.querySelectorAll('title')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",  # pylint: disable=line-too-long
    "description": "() => [...document.querySelectorAll('meta[name=description]')].map( el => {return {'element':xpath(el), 'content': el.content};})",  # pylint: disable=line-too-long
    "h1": "() => [...document.querySelectorAll('h1')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",  # pylint: disable=line-too-long
    "h2": "() => [...document.querySelectorAll('h2')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",  # pylint: disable=line-too-long
    "links": "() => [...document.querySelectorAll('a')].map( el => {return {'element':xpath(el), 'content': {'href': el.href, 'text': el.textContent, 'rel':el.rel}};})",  # pylint: disable=line-too-long
    "images": "() => [...document.querySelectorAll('img')].map( el => {return {'element':xpath(el), 'content': {'src': el.src, 'alt': el.alt}};})",  # pylint: disable=line-too-long
    "canonical": "() => [...document.querySelectorAll('link[rel=canonical]')].map( el => {return {'element':xpath(el), 'content': el.href};})",  # pylint: disable=line-too-long
    "robots": "() => [...document.querySelectorAll('meta[name=robots]')].map( el => {return {'element':xpath(el), 'content': el.content};})",  # pylint: disable=line-too-long
    "schema": "() => [...document.querySelectorAll('script[type=\"application/ld+json\"]')].map( el => {return {'element':xpath(el), 'content': JSON.parse(el.textContent)};})",  # pylint: disable=line-too-long
}
"""

# Various extractions to run on Chrome.
EXTRACTIONS = {
    "title": "() => [...document.querySelectorAll('title')].map( el => {return el.textContent;})",  # pylint: disable=line-too-long
    "description": "() => [...document.querySelectorAll('meta[name=description]')].map( el => {return el.content;})",  # pylint: disable=line-too-long
    "h1": "() => [...document.querySelectorAll('h1')].map( el => {return el.textContent;})",  # pylint: disable=line-too-long
    "h2": "() => [...document.querySelectorAll('h2')].map( el => {return el.textContent;})",  # pylint: disable=line-too-long
    "links": "() => [...document.querySelectorAll('a')].map( el => {return el.href;})",  # pylint: disable=line-too-long
    "images": "() => [...document.querySelectorAll('img')].map( el => {return el.src;})",  # pylint: disable=line-too-long
    "canonical": "() => [...document.querySelectorAll('link[rel=canonical]')].map( el => {return el.href;})",  # pylint: disable=line-too-long
    "robots": "() => [...document.querySelectorAll('meta[name=robots]')].map( el => {return el.content;})",  # pylint: disable=line-too-long
    "schema": "() => [...document.querySelectorAll('script[type=\"application/ld+json\"]')].map( el => {return JSON.parse(el.textContent);})",  # pylint: disable=line-too-long
}

# Helper Scripts to include in document on page launch.
DOCUMENT_SCRIPTS = """() => {

 window.xpath = (elt) => {
        var path = "" ,
    		getElementIdx = function(elt) {
    	    	var before = 1 ,
    				after = 0 ;
    	    	for (var sib = elt.previousSibling; sib ; sib = sib.previousSibling) {
    		        if(sib.nodeType == 1 && sib.tagName == elt.tagName)	before++
       			}
    	    	for (var sib = elt.nextSibling; sib ; sib = sib.nextSibling) {
    		        if(sib.nodeType == 1 && sib.tagName == elt.tagName)	after++
       			}
    	    	if( before == 1 && after == 0 )
    				return 0 ;
    			else
    				return before ;
    		} ;

        for (; elt && elt.nodeType == 1; elt = elt.parentNode) {
    	   	idx = getElementIdx(elt);
    		xname = elt.tagName;
    		if (idx > 0) xname += "[" + idx + "]";
    		path = "/" + xname + path;
        }

        return path.toLowerCase() ;
    }


    // Calculate LCP
    window.largestContentfulPaint = 0;

    const observer1 = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        const lastEntry = entries[entries.length - 1];
        window.largestContentfulPaint = lastEntry.renderTime || lastEntry.loadTime;
    });

    observer1.observe({type: 'largest-contentful-paint', buffered: true});


    // Calculate CLS
    window.cumulativeLayoutShiftScore = 0;

    const observer2 = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries();
        for (const entry of entries) {
            window.cumulativeLayoutShiftScore += entry.value;
        }
    });

    observer2.observe({type: 'layout-shift', buffered: true});


    // All Observers
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
          observer1.takeRecords();
          observer1.disconnect();
          observer2.takeRecords();
          observer2.disconnect();
        }
    });

}
"""  # noqa

# Regular3G is a good way to remove variance by downgrading all loads to consistently slow.
NETWORK_PRESETS = {
    "GPRS": {
        "offline": False,
        "downloadThroughput": 6400,
        "uploadThroughput": 2560,
        "latency": 500,
    },
    "Regular2G": {
        "offline": False,
        "downloadThroughput": 32000,
        "uploadThroughput": 6400,
        "latency": 300,
    },
    "Good2G": {
        "offline": False,
        "downloadThroughput": 57600,
        "uploadThroughput": 19200,
        "latency": 150,
    },
    "Regular3G": {
        "offline": False,
        "downloadThroughput": 96000,
        "uploadThroughput": 32000,
        "latency": 100,
    },
    "Good3G": {
        "offline": False,
        "downloadThroughput": 196608,
        "uploadThroughput": 96000,
        "latency": 40,
    },
    "Regular4G": {
        "offline": False,
        "downloadThroughput": 524288,
        "uploadThroughput": 393216,
        "latency": 20,
    },
    "DSL": {
        "offline": False,
        "downloadThroughput": 262144,
        "uploadThroughput": 131072,
        "latency": 5,
    },
    "WiFi": {
        "offline": False,
        "downloadThroughput": 3932160,
        "uploadThroughput": 1966080,
        "latency": 2,
    },
}


def format_results(data):

    return {
        "status": dot_get("status", data),
        "headers": dot_get("headers", data),
        "content": {
            "canonical": dot_get("canonical", data),
            "robots": dot_get("robots", data),
            "title": dot_get("title", data),
            "meta_description": dot_get("description", data),
            "h1": dot_get("h1", data),
            "h2": dot_get("h2", data),
            "links": dot_get("links", data),
            "images": dot_get("images", data),
            "schema": dot_get("schema", data),
        },
        "performance": {
            "nodes": dot_get("metrics.performanceMetrics.Nodes", data),
            "resources": dot_get("metrics.performanceMetrics.Resources", data),
            "layout_duration": dot_get(
                "metrics.performanceMetrics.LayoutDuration", data
            ),
            "recalc_style_duration": dot_get(
                "metrics.performanceMetrics.RecalcStyleDuration", data
            ),
            "script_duration": dot_get(
                "metrics.performanceMetrics.ScriptDuration", data
            ),
            "v8_compile_duration": dot_get(
                "metrics.performanceMetrics.V8CompileDuration", data
            ),
            "task_duration": dot_get("metrics.performanceMetrics.TaskDuration", data),
            "task_other_duration": dot_get(
                "metrics.performanceMetrics.TaskOtherDuration", data
            ),
            "thread_time": dot_get("metrics.performanceMetrics.ThreadTime", data),
            "jd_heap_used_size": dot_get(
                "metrics.performanceMetrics.JSHeapUsedSize", data
            ),
            "js_heap_total_size": dot_get(
                "metrics.performanceMetrics.JSHeapTotalSize", data
            ),
            "time_to_first_byte": dot_get("metrics.calculated.timeToFirstByte", data),
            "first_paint": dot_get("metrics.calculated.firstPaint", data),
            "first_contentful_paint": dot_get(
                "metrics.calculated.firstContentfulPaint", data
            ),
            "largest_contentful_paint": dot_get(
                "metrics.calculated.largestContentfulPaint", data
            ),
            "time_to_interactive": dot_get(
                "metrics.calculated.timeToInteractive", data
            ),
            "dom_content_loaded": dot_get("metrics.calculated.domContentLoaded", data),
            "dom_complete": dot_get("metrics.calculated.domComplete", data),
            "cumulative_layout_shift": dot_get(
                "metrics.calculated.cumulativeLayoutShift", data
            ),
        },
        "coverage": {
            "summary": {
                "total_unused": dot_get("coverage.summary.totalUnused", data),
                "total_bytes": dot_get("coverage.summary.totalBytes", data),
                "unused_pc": dot_get("coverage.summary.totalUnusedPc", data),
            },
            "css": {
                "total_unused": dot_get("coverage.css.summary.totalUnused", data),
                "total_bytes": dot_get("coverage.css.summary.totalBytes", data),
                "unused_pc": dot_get("coverage.css.summary.totalUnusedPc", data),
            },
            "js": {
                "total_unused": dot_get("coverage.js.summary.totalUnused", data),
                "total_bytes": dot_get("coverage.js.summary.totalBytes", data),
                "unused_pc": dot_get("coverage.js.summary.totalUnusedPc", data),
            },
        },
    }


def parse_numerical_dict(data, r=2):
    """Converts dict with numerical values to consistent `r` rounded float values."""
    return {k: round(float(v), r) for k, v in data.items()}


# Performance Timing Functions
def parse_performance_timing(p_timing):
    """Changes performance timing results to deltas."""
    ns = p_timing["navigationStart"]
    return {k: v - ns if v else 0 for k, v in p_timing.items()}


def parse_ranges(ranges):
    """Helper function to parse coverage data ranges."""
    total_length = 0

    for single_range in ranges:
        (start, end) = single_range.values()
        length = end - start
        total_length = total_length + length

    return total_length


# Coverage Functions
def parse_coverage_objects(coverage):
    """Helper function for parse_coverage to calulate separate asset coverage."""
    total_unused = 0
    total_bytes = 0
    results = []

    for file in coverage:

        (url, ranges, text) = file.values()

        used = parse_ranges(ranges)
        total = len(text)

        unused = total - used

        unused_pct = round(((unused + 1) / (total + 1)) * 100, 2)

        results.append(
            {
                "url": quote_plus(url),
                "total": total,
                "unused": unused,
                "unusedPc": unused_pct,
            }
        )

        total_unused = total_unused + unused
        total_bytes = total_bytes + total

    total_unused_pct = round(((total_unused + 1) / (total_bytes + 1)) * 100, 2)

    return {
        "results": results,
        "summary": {
            "totalUnused": float(total_unused),
            "totalBytes": float(total_bytes),
            "totalUnusedPc": float(total_unused_pct),
        },
    }


def parse_coverage(coverage_js, coverage_css):
    """Organizes to dict Chrome coverage report."""
    parsed_js_coverage = parse_coverage_objects(coverage_js)
    parsed_css_coverage = parse_coverage_objects(coverage_css)

    total_unused = (
        parsed_js_coverage["summary"]["totalUnused"]
        + parsed_css_coverage["summary"]["totalUnused"]
    )
    total_bytes = (
        parsed_js_coverage["summary"]["totalBytes"]
        + parsed_css_coverage["summary"]["totalBytes"]
    )

    total_unused_pct = round(((total_unused + 1) / (total_bytes + 1)) * 100, 2)

    return {
        "summary": {
            "totalBytes": float(total_unused),
            "totalUnused": float(total_bytes),
            "totalUnusedPc": float(total_unused_pct),
        },
        "css": parsed_css_coverage,
        "js": parsed_js_coverage,
    }
