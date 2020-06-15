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

from pyppeteer.errors import NetworkError
from pyppeteer import launch

from seodeploy.lib.logging import get_logger
from seodeploy.lib.config import Config

from seodeploy.modules.headless.exceptions import URLMissingException
from seodeploy.modules.headless.helpers import (
    format_results,
    parse_numerical_dict,
    parse_performance_timing,
    parse_coverage,
)
from seodeploy.modules.headless.helpers import (
    USER_AGENT,
    NETWORK_PRESETS,
    DOCUMENT_SCRIPTS,
    EXTRACTIONS,
)


_LOG = get_logger(__name__)


class HeadlessChrome:
    """Class which handles rendering and extraction using Chrome Browser and CDP"""

    def __init__(self, config=None):

        self.browser = None
        self.page = None
        self.coverage = None
        self.client = None
        self.config = config or Config(module="headless")
        self.network = self.config.headless.NETWORK_PRESET or "Regular3G"

        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(self.build_browser())

    async def build_browser(self):
        """Publicly accessible build browser function."""

        # browser = await launch()
        browser = await launch(args=["--no-sandbox"], headless=True)

        self.browser = await browser.createIncognitoBrowserContext()

    def render(self, url):
        """Publicly accessible render function."""

        result = {"page_data": None, "error": None}

        # Multiple tries (3)
        for _ in range(3):
            try:
                result["page_data"] = format_results(
                    asyncio.get_event_loop().run_until_complete(self._render(url))
                )
                break

            except NetworkError:
                # _LOG.error('Network Error trying url: ', url)
                asyncio.set_event_loop(asyncio.new_event_loop())

            except URLMissingException:
                error = "A valid URL was not supplied: " + url
                _LOG.error(error)
                result["error"] = error
                break

        else:
            error = "Max tries exhausted for: " + url
            _LOG.error(error)
            result["error"] = error

        return result

    async def _render(self, url):
        """Main render function. Builds page and executes extraction."""

        if not url:
            raise URLMissingException("A URL is required to render.")

        await self._build_page(url)

        dom = {}

        for key, expression in EXTRACTIONS.items():
            dom[key] = await self.page.evaluate(expression)

        dom["metrics"] = await self._extract_performance_metrics()
        dom["coverage"] = self._extract_coverage()

        # This removes elements from the page -- run last.
        dom["content"] = await self._extract_content()

        await self._close_page()

        return dom

    async def _build_page(self, url):
        """Main method to build page, setup reports, and navigate to URL"""

        self.page = await self.browser.newPage()
        await self.page.setBypassCSP(True)  # Ignore content security issues.
        await self.page.setUserAgent(USER_AGENT)
        await self.page.setViewport({"width": 360, "height": 640, "isMobile": True})
        await self.page.evaluateOnNewDocument(DOCUMENT_SCRIPTS)

        self.client = await self.page.target.createCDPSession()
        self.coverage = {}

        # Limit network to cosistent slow.
        await self.client.send(
            "Network.emulateNetworkConditions", NETWORK_PRESETS[self.network]
        )

        # Enable performance reporting
        await self.client.send("Performance.enable")

        await self.page.coverage.startJSCoverage()
        await self.page.coverage.startCSSCoverage()

        # Authenticate if Staging and user/pass defined.
        await self._check_auth(url)

        await self.page.goto(url, waitUntil="networkidle2", timeout=60000)

        self.coverage["JSCoverage"] = await self.page.coverage.stopJSCoverage()
        self.coverage["CSSCoverage"] = await self.page.coverage.stopCSSCoverage()

        # Small wait to ensure all is complete.
        await self.page.waitFor(1000)

    async def _close_page(self):
        """Close page and relevant class data after page load"""

        await self.page.close()
        self.page = None
        self.coverage = None

    async def _check_auth(self, url):
        """Authenticate if Staging and user/pass defined."""

        username = self.config.headless.STAGE_AUTH_USER
        password = self.config.headless.STAGE_AUTH_PASS
        stage_host = self.config.headless.STAGE_HOST

        if username and password and stage_host in url:
            await self.page.authenticate({"username": username, "password": password})

    async def _extract_content(self):
        """Extracts content from the page.  Since this destroys the DOM, it should be run last."""

        await self.page.evaluate(
            "document.querySelectorAll('script, iframe, style, noscript, link').forEach(function(el){el.remove()})",
            force_expr=True,
        )
        content = await self.page.evaluate("document.body.textContent", force_expr=True)
        return " ".join(content.split()).strip().lower()

    async def _extract_performance_metrics(self):
        """Pull timing and calculated metrics from rendered page"""

        metrics = {}

        # Page Metrics #NOTE: Removing this because no current additive value.
        # page_metrics = await self.page.metrics()
        # metrics['pageMetrics'] = parse_numerical_dict(page_metrics)

        # Performance Metrics
        perf_metrics = await self.client.send("Performance.getMetrics")
        metrics["performanceMetrics"] = parse_numerical_dict(
            {i["name"]: i["value"] for i in perf_metrics["metrics"] if "name" in i}
        )

        # Timing Metrics
        timing_metrics = await self.page.evaluate(
            "() => {return JSON.parse(JSON.stringify(window.performance.timing));}"
        )
        metrics["timing"] = parse_numerical_dict(
            parse_performance_timing(timing_metrics)
        )

        # Calculated Metrics
        calculated = await self._calculated_metrics(metrics)
        metrics["calculated"] = parse_numerical_dict(calculated)

        return metrics

    async def _calculated_metrics(self, metrics):
        """Extract and caculate important performance metrics"""

        result = {}
        expressions = {
            "timeToFirstByte": (metrics["timing"]["responseStart"],),
            "firstPaint": "() => {return performance.getEntriesByName('first-paint')[0].startTime;}",
            "firstContentfulPaint": "() => {return performance.getEntriesByName('first-contentful-paint')[0].startTime;}",  # noqa
            "largestContentfulPaint": "() => {return window.largestContentfulPaint;}",
            "timeToInteractive": (metrics["timing"]["domInteractive"],),
            "domContentLoaded": (metrics["timing"]["domContentLoadedEventStart"],),
            "domComplete": (metrics["timing"]["domComplete"],),
            "cumulativeLayoutShift": "() => {return window.cumulativeLayoutShiftScore;}",
        }

        for key, expression in expressions.items():
            if isinstance(expression, str):
                result[key] = await self.page.evaluate(expression)
            else:
                result[key] = expression[0]

        return result

    def _extract_coverage(self):
        """Handler function to parse coverage from CDP session"""
        return parse_coverage(self.coverage["JSCoverage"], self.coverage["CSSCoverage"])


def render_url(url):
    chrome = HeadlessChrome()
    return chrome.render(url)
