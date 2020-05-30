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

from functools import reduce
from urllib.parse import quote_plus


# User Agent for requests TODO: Should probably move this to YAML config file.
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"


# Various extractions to run on Chrome.
EXTRACTIONS = {
    "title": "() => [...document.querySelectorAll('title')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",
    "description": "() => [...document.querySelectorAll('meta[name=description]')].map( el => {return {'element':xpath(el), 'content': el.content};})",
    "h1": "() => [...document.querySelectorAll('h1')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",
    "h2": "() => [...document.querySelectorAll('h2')].map( el => {return {'element':xpath(el), 'content': el.textContent};})",
    "links": "() => [...document.querySelectorAll('a')].map( el => {return {'element':xpath(el), 'content': {'href': el.href, 'text': el.textContent, 'rel':el.rel}};})",
    "images": "() => [...document.querySelectorAll('img')].map( el => {return {'element':xpath(el), 'content': {'src': el.src, 'alt': el.alt}};})",
    "canonical": "() => [...document.querySelectorAll('link[rel=canonical]')].map( el => {return {'element':xpath(el), 'content': el.href};})",
    "robots": "() => [...document.querySelectorAll('meta[name=robots]')].map( el => {return {'element':xpath(el), 'content': el.content};})",
    "schema": "() => [...document.querySelectorAll('script[type=\"application/ld+json\"]')].map( el => {return {'element':xpath(el), 'content': JSON.parse(el.textContent)};})",
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
"""

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
    def get(dot_not):
        return reduce(dict.get, dot_not.split("."), data)

    return {
        "content": {
            "canonical": get("canonical"),
            "robots": get("robots"),
            "title": get("title"),
            "meta_description": get("description"),
            "h1": get("h1"),
            "h2": get("h2"),
            "links": get("links"),
            "images": get("images"),
            "schema": get("schema"),
        },
        "performance": {
            "nodes": get("metrics.performanceMetrics.Nodes"),
            "resources": get("metrics.performanceMetrics.Resources"),
            "layout_duration": get("metrics.performanceMetrics.LayoutDuration"),
            "recalc_style_duration": get(
                "metrics.performanceMetrics.RecalcStyleDuration"
            ),
            "script_duration": get("metrics.performanceMetrics.ScriptDuration"),
            "v8_compile_duration": get("metrics.performanceMetrics.V8CompileDuration"),
            "task_duration": get("metrics.performanceMetrics.TaskDuration"),
            "task_other_duration": get("metrics.performanceMetrics.TaskOtherDuration"),
            "thread_time": get("metrics.performanceMetrics.ThreadTime"),
            "jd_heap_used_size": get("metrics.performanceMetrics.JSHeapUsedSize"),
            "js_heap_total_size": get("metrics.performanceMetrics.JSHeapTotalSize"),
            "time_to_first_byte": get("metrics.calculated.timeToFirstByte"),
            "first_paint": get("metrics.calculated.firstPaint"),
            "first_contentful_paint": get("metrics.calculated.firstContentfulPaint"),
            "largest_contentful_paint": get(
                "metrics.calculated.largestContentfulPaint"
            ),
            "time_to_interactive": get("metrics.calculated.timeToInteractive"),
            "dom_content_loaded": get("metrics.calculated.domContentLoaded"),
            "dom_complete": get("metrics.calculated.domComplete"),
            "cumulative_layout_shift": get("metrics.calculated.cumulativeLayoutShift"),
        },
        "coverage": {
            "summary": {
                "total_unused": get("coverage.summary.totalUnused"),
                "total_bytes": get("coverage.summary.totalBytes"),
                "unused_pc": get("coverage.summary.totalUnusedPc"),
            },
            "css": {
                "total_unused": get("coverage.css.summary.totalUnused"),
                "total_bytes": get("coverage.css.summary.totalBytes"),
                "unused_pc": get("coverage.css.summary.totalUnusedPc"),
            },
            "js": {
                "total_unused": get("coverage.js.summary.totalUnused"),
                "total_bytes": get("coverage.js.summary.totalBytes"),
                "unused_pc": get("coverage.js.summary.totalUnusedPc"),
            },
        },
    }


def parse_numerical_dict(data, r=2):
    result = {}
    for k, v in data.items():
        if isinstance(v, str):
            v = float(v) if "." in v else int(v)

        if isinstance(v, float):
            result[k] = round(v, r)
        else:
            result[k] = int(v)

    return result


# Performance Timing Functions
def parse_performance_timing(p_timing):
    ns = p_timing["navigationStart"]
    return {k: v - ns if v else 0 for k, v in p_timing.items()}


# Coverage Functions
def parse_coverage_objects(coverage, typ):

    totalUnused = 0
    totalBytes = 0
    results = []

    for file in coverage:

        (url, ranges, text) = file.values()

        totalLength = 0

        for range in ranges:
            (start, end) = range.values()
            length = end - start
            totalLength = totalLength + length

        total = len(text)
        unused = total - totalLength

        unusedPc = round(((unused + 1) / (total + 1)) * 100, 2)

        results.append(
            {
                "url": quote_plus(url),
                "total": total,
                "unused": unused,
                "unusedPc": unusedPc,
            }
        )

        totalUnused = totalUnused + unused
        totalBytes = totalBytes + total

    totalUnusedPc = round(((totalUnused + 1) / (totalBytes + 1)) * 100, 2)

    return {
        "results": results,
        "summary": {
            "totalUnused": totalUnused,
            "totalBytes": totalBytes,
            "totalUnusedPc": totalUnusedPc,
        },
    }


def parse_coverage(coverageJS, coverageCSS):

    parsedJSCoverage = parse_coverage_objects(coverageJS, "JS")
    parsedCSSCoverage = parse_coverage_objects(coverageCSS, "CSS")

    totalUnused = (
        parsedJSCoverage["summary"]["totalUnused"]
        + parsedCSSCoverage["summary"]["totalUnused"]
    )
    totalBytes = (
        parsedJSCoverage["summary"]["totalBytes"]
        + parsedCSSCoverage["summary"]["totalBytes"]
    )
    unusedPc = round(((totalUnused + 1) / (totalBytes + 1)) * 100, 2)

    return {
        "summary": {
            "totalBytes": totalBytes,
            "totalUnused": totalUnused,
            "totalUnusedPc": unusedPc,
        },
        "css": parsedCSSCoverage,
        "js": parsedJSCoverage,
    }
