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


import asyncio
import threading
import nest_asyncio

import os
os.environ["PYPPETEER_CHROMIUM_REVISION"] = "769582" # TODO: Move out to config file.

from pyppeteer.errors import NetworkError
from pyppeteer import launch

from lib.logging import get_logger # TODO: Fix this
from .exceptions import HeadlessException, URLMissingException
from .extract import EXTRACTIONS, DOCUMENT_SCRIPTS, NETWORK_LIMITING, USER_AGENT
from .functions import parse_coverage, parse_performance_timing, parse_numerical_dict


_LOG = get_logger(__name__)

try:
    get_ipython().config
    nest_asyncio.apply()
except NameError:
    pass


class HeadlessChrome():

    def __init__(self, config=None):

        self.browser = None
        self.page = None
        self.coverage = {}
        self.client = None

        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self.build_browser())
        print('Browser Built')

    async def build_browser(self):
        # browser = await launch()
        browser = await launch( args=['--no-sandbox'],
                                headless=True
                               )

        self.browser = await browser.createIncognitoBrowserContext()


    def render(self,  url=None):

        # Multiple tries (3)
        for _ in range(3):
            try:
                return asyncio.get_event_loop().run_until_complete(self._render(url))

            except NetworkError:
                #_LOG.error('Network Error trying url: ', url)
                asyncio.set_event_loop(asyncio.new_event_loop())
                asyncio.get_event_loop().run_until_complete(self._build_page(url))

            except URLMissingException:
                _LOG.error('A valid URL was not supplied: ', url)
                break


    async def _render(self, url):

        if not url:
            raise URLMissingException('A URL is required to render.')

        await self._build_page(url)
        print("Navigating to:", url, "\n")

        dom = {}

        for key, expression in EXTRACTIONS.items():
            dom[key] = await self.page.evaluate(expression)

        dom['metrics'] = await self._extract_performance_metrics()
        dom['coverage'] = self._extract_coverage()

        # This removes elements from the page -- run last.
        dom['content'] = await self._extract_content()

        await self._close_page()

        return dom


    async def _build_page(self, url):

        self.page = await self.browser.newPage()
        await self.page.setBypassCSP(True) # Ignore content security issues.
        await self.page.setUserAgent(USER_AGENT)
        await self.page.setViewport({"width": 360, "height": 640, "isMobile": True})
        await self.page.evaluateOnNewDocument(DOCUMENT_SCRIPTS)

        self.client = await self.page.target.createCDPSession();

        # Limit network to cosistent slow.
        await self.client.send('Network.emulateNetworkConditions', NETWORK_LIMITING)

        # Enable performance reporting
        await self.client.send('Performance.enable');

        await self.page.coverage.startJSCoverage()
        await self.page.coverage.startCSSCoverage()

        await self.page.goto(url, waitUntil='networkidle2', timeout=60000)

        self.coverage['JSCoverage'] = await self.page.coverage.stopJSCoverage()
        self.coverage['CSSCoverage'] = await self.page.coverage.stopCSSCoverage()

        # Small wait to ensure all is complete.
        await self.page.waitFor(1000);


    async def _close_page(self):
        await self.page.close()
        self.page = None
        self.coverage = None


    async def _extract_content(self):
        await self.page.evaluate("document.querySelectorAll('script, iframe, style, noscript, link').forEach(function(el){el.remove()})", force_expr=True)
        content = await self.page.evaluate("document.body.textContent", force_expr=True)
        return ' '.join(content.split()).strip().lower()


    async def _extract_performance_metrics(self):

        metrics = {}

        # Page Metrics #NOTE: Removing this because no current additive value.
        # page_metrics = await self.page.metrics()
        # metrics['pageMetrics'] = parse_numerical_dict(page_metrics)

        # Performance Metrics
        perf_metrics = await self.client.send('Performance.getMetrics');
        metrics['performanceMetrics'] = parse_numerical_dict({i['name']:i['value'] for i in perf_metrics['metrics'] if 'name' in i})

        # Timing Metrics
        timing_metrics = await self.page.evaluate("() => {return JSON.parse(JSON.stringify(window.performance.timing));}")
        metrics['timing'] = parse_numerical_dict(parse_performance_timing(timing_metrics))

        # Calculated Metrics
        calculated = await self._calculated_metrics(metrics)
        metrics['calculated'] = parse_numerical_dict(calculated)

        return metrics


    async def _calculated_metrics(self, metrics):
        result = {}
        expressions = {
                    'timeToFirstByte':          (metrics['timing']['responseStart'], ),
                    'firstPaint':               "() => {return performance.getEntriesByName('first-paint')[0].startTime;}",
                    'firstContentfulPaint':     "() => {return performance.getEntriesByName('first-contentful-paint')[0].startTime;}",
                    'largestContentfulPaint':   "() => {return window.largestContentfulPaint;}",
                    'timeToInteractive':        (metrics['timing']['domInteractive'], ),
                    'domContentLoaded':         (metrics['timing']['domContentLoadedEventStart'], ),
                    'domComplete':              (metrics['timing']['domComplete'], ),
                    'cumulativeLayoutShift':    "() => {return window.cumulativeLayoutShiftScore;}",
                    }

        for key, expression in expressions.items():
            if isinstance(expression, str):
                result[key] = await self.page.evaluate(expression)
            else:
                result[key] = expression[0]

        return {k:v for k,v in result.items()}


    def _extract_coverage(self):
        return parse_coverage(self.coverage['JSCoverage'], self.coverage['CSSCoverage'])


def render_url(url):
    chrome = HeadlessChrome()
    return chrome.render(url)
