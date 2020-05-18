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

'''
Using: https://github.com/miyakogi/pyppeteer
Sample:
import asyncio
from pyppeteer import launch
async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://locomotive.agency/')
    await page.screenshot({'path': 'locomotive.png'})
    dimensions = await page.evaluate('() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }')
    print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    await browser.close()
asyncio.get_event_loop().run_until_complete(main())
'''

import asyncio
import threading
import nest_asyncio

import os
os.environ["PYPPETEER_CHROMIUM_REVISION"] = "769582"

from pyppeteer.errors import NetworkError
from pyppeteer import launch

#from lib.logging import get_logger
from exceptions import HeadlessException, URLMissingException
from extract import EXTRACTIONS, DOCUMENT_SCRIPTS
from functions import parse_coverage, parse_performance_timing, parse_numerical_dict

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"

#_LOG = get_logger(__name__)

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
                                headless=True,
                                devtools=True
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
                asyncio.get_event_loop().run_until_complete(self.build_page())

            except URLMissingException:
                #_LOG.error('A valid URL was not supplied: ', url)
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
        await self.client.send('Performance.enable');

        await self.page.coverage.startJSCoverage()
        await self.page.coverage.startCSSCoverage()

        await self.page.goto(url, waitUntil='networkidle2', timeout=60000)

        self.coverage['JSCoverage'] = await self.page.coverage.stopJSCoverage()
        self.coverage['CSSCoverage'] = await self.page.coverage.stopCSSCoverage()

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

        # Page Metrics
        page_metrics = await self.page.metrics()
        metrics['pageMetrics'] = parse_numerical_dict(page_metrics)

        # Performance Metrics
        perf_metrics = await self.client.send('Performance.getMetrics');
        metrics['performanceMetrics'] = parse_numerical_dict({i['name']:i['value'] for i in perf_metrics['metrics'] if 'name' in i})

        # Timing Metrics
        t_metrics = await self.page.evaluate("() => {return JSON.parse(JSON.stringify(window.performance.timing));}")
        metrics['timing'] = parse_numerical_dict(parse_performance_timing(t_metrics))

        # Calculated Metrics
        calculated = await self._calculated_metrics()
        metrics['calculated'] = parse_numerical_dict(calculated)

        return metrics


    async def _calculated_metrics(self):
        metrics = {}
        expressions = {
                    'firstPaint':               "() => {return performance.getEntriesByName('first-paint')[0].startTime;}",
                    'firstContentfulPaint':     "() => {return performance.getEntriesByName('first-contentful-paint')[0].startTime;}",
                    'largestContentfulPaint':   "() => {return window.largestContentfulPaint;}",
                    'cumulativeLayoutShift':    "() => {return window.cumulativeLayoutShiftScore;}",
                    }

        for key, expression in expressions.items():
            metrics[key] = await self.page.evaluate(expression)

        return {k:v for k,v in metrics.items()}


    def _extract_coverage(self):
        return parse_coverage(self.coverage['JSCoverage'], self.coverage['CSSCoverage'])




def render_url(url):
    chrome = HeadlessChrome()
    return chrome.render(url)

if __name__ == "__main__":
    import json
    print(json.dumps(render_url('https://locomotive.agency/'), indent=2))
