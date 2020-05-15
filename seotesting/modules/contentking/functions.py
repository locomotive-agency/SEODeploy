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

from urllib.parse import urljoin
from datetime import datetime

import json
import time
import requests
from tqdm.auto import tqdm

import pandas as pd

from seotesting.lib.logging  import get_logger
from .exceptions import ContentKingAPIError, ContentKingMissing
from seotesting.lib.helpers import group_batcher, mp_list_map


_LOG = get_logger(__name__)


def load_report(report, config, **data):
    '''
        Description: Receives a report type and names parameters passed to function.
        Requests from ContentKing Reporting API.

        Reporting API Details: https://www.contentkingapp.com/support/reporting-api/

        Implemeneted Reports:
            * websites
            * alerts
            * issues
            * segments
            * statistics
            * statistics:segment
            * url

        Implemented Named Parameters:
            * id: COntentKing ID of website (string)
            * url: URL of page to get details about. (string)
            * per_page: How many pages to return at a time from the `pages` endpoint. Max is 500, (integer)


        TODO:
            * Currently there is minimal error handling.
            * Should this be turned into a class?
            * Need to add rate limit to generator function `get_paged_reports`.

    '''

    def api_reports(report, data=None):
        reports = {
            'websites': 'websites',
            'alerts': 'websites/{id}/alerts',
            'issues': 'websites/{id}/issues',
            'segments': 'websites/{id}/segments',
            'statistics': 'websites/{id}/statistics/website',
            'statistics:segment': 'websites/{id}/statistics/segment:{segment_id}',
            'url': 'websites/{id}/pages?url={url}',
            'pages': 'websites/{id}/pages/list'
        }
        return reports.get(report, "404").format(**data)

    def get_report(report, config, data, query_string=None):

        api_url = urljoin(config.contentking.ENDPOINT, api_reports(report, data))

        headers = {
            'User-Agent': 'Python CI/CD Testing',
            'Authorization': 'token {}'.format(config.contentking.REPORT_API_KEY),
            'Content-Type': 'application/json'
        }

        tries = 3
        for i in range(tries):

            try:
                response = requests.get(api_url, params=query_string, headers=headers, timeout=config.contentking.API_TIMEOUT, verify=False)
                # Raise HTTPError if not 20X
                response.raise_for_status()
                break

            except requests.exceptions.Timeout as e:
                _LOG.error(str(e))
                time.sleep((i + 1) * 10)

            # Not sure why Requests throws this instead of `Timeout` for timeouts.
            except requests.exceptions.ConnectionError as e:
                _LOG.error(str(e))
                time.sleep((i + 1) * 10)

            except requests.exceptions.HTTPError as e:
                api_message = response.json()['message']
                _LOG.error("{} ({})".format(str(e), api_message))
                break

            # If it is an unknown error, let's break and raise exception.
            except Exception as e:
                _LOG.error('Unspecified ContentKing Error:' + str(e))
                raise ContentKingAPIError(str(e))

        if response and response.status_code == 200:
            return response.json()

        return None

    def get_paged_report(report, config, data):
        page = 1
        per_page = data.get('per_page', 100)
        while True:
            query_string = {'page': page, 'per_page': per_page}

            result = get_report(report, config, data, query_string=query_string)

            if result:
                urls = result['urls']
                yield urls

                time.sleep(2)  # Arbitrarily selected wait.

                if len(urls) < per_page:
                    break

                page += 1

            else:
                yield []
                break

    paged_reports = ['pages']

    if report in paged_reports:
        return get_paged_report(report, config, data)

    return get_report(report, config, data)


def _notify_change(url, config):

    api_url = urljoin(config.contentking.ENDPOINT, 'check_url')

    headers = {
        'User-Agent': 'Python CI/CD Testing',
        'Authorization': 'token {}'.format(config.contentking.CMS_API_KEY),
        'Content-Type': 'application/json',
    }

    data = json.dumps({"url": url})

    tries = 3
    for i in range(tries):

        try:
            response = requests.post(api_url, data=data, headers=headers, timeout=config.contentking.API_TIMEOUT, verify=False)
            # Raise HTTPError if not 20X
            response.raise_for_status()
            break

        except requests.exceptions.Timeout as e:
            _LOG.error(str(e))
            time.sleep((i + 1) * 10)

        # Not sure why Requests throws this instead of `Timeout` for timeouts.
        except requests.exceptions.ConnectionError as e:
            _LOG.error(str(e))
            time.sleep((i + 1) * 10)

        except requests.exceptions.HTTPError as e:
            api_message = response.json()['message']
            _LOG.error("{} ({})".format(str(e), api_message))
            break

        # Just want to catch any other errors to the log, so we can add in here.
        except Exception as e:
            _LOG.error('Unspecified Error:' + str(e))
            break

    if response and response.status_code == 200:
        return response.json()

    return None


def ping_prod_paths(paths, config):

    results = {}
    for path in paths:
        url = urljoin(config.contentking.PROD_HOST, path)
        result = _notify_change(url, config)

        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results


def ping_stage_paths(paths, config):

    results = {}
    for path in paths:
        url = urljoin(config.contentking.STAGE_HOST, path)
        result = _notify_change(url, config)

        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results


def run_path_pings(sample_paths, config):

    """Pings ContentKing with Paths across both staging and production websites.

    Parameters
    ----------
    sample_paths: list
        List of paths to check.
    """

    # Ping Content King for Production and Staging URLs
    batches = [b for b in group_batcher(sample_paths, list, config.contentking.BATCH_SIZE, fill=None)]
    prod_ping_results = {}
    stage_ping_results = {}

    for batch in tqdm(batches, desc="Pinging API Production and Staging URLs"):
        prod_ping_results.update(ping_prod_paths(batch, config))
        stage_ping_results.update(ping_stage_paths(batch, config))

    # Check results were pinged correctly.
    sent_total = len(sample_paths)
    prod_sent_errors, stage_sent_errors = True, True

    # Check results
    if prod_ping_results:
        sent_percent = round((len([k for k,v in prod_ping_results.items() if v == 'ok']) / sent_total) * 100, 2)
        _LOG.info("{}% of production URLs successfully sent.".format(sent_percent))

        if sent_percent < 100:
            prod_sent_errors = [k for k,v in prod_ping_results.items() if v == 'error']
            for e in prod_sent_errors:
                _LOG.error("Production URL Ping Error: {}".format(e))
        else:
            prod_sent_errors = False
    else:
        _LOG.error("No results from Production pings.")

    if stage_ping_results:
        sent_percent = round((len([k for k,v in stage_ping_results.items() if v == 'ok']) / sent_total) * 100, 2)
        _LOG.info("{}% of staging URLs successfully sent.".format(sent_percent))

        if sent_percent < 100:
            stage_sent_errors = [k for k,v in stage_ping_results.items() if v == 'error']
            for e in stage_sent_errors:
                _LOG.error("Staging URL Ping Error: {}".format(e))
        else:
            stage_sent_errors = False

    else:
        _LOG.error("No results from Staging pings.")

    if prod_sent_errors or stage_sent_errors:
        raise ContentKingAPIError("There were issues sending the production and/or staging URLs to COntentKing.  Please check the error log.")

    return True


def _check_results(paths, config=None, data=None):

    """Loads path data from ContentKing and returns cleaned data report.
       Checks to see if the latest crawl timestamp is more recent than when this process started.

    """

    unchecked = paths.copy()
    results = []

    time_zone = data['time_zone']
    start_time = data['start_time']
    time_col = data['time_col']


    while unchecked:

        # Grab the first
        path = unchecked.pop(0)

        url = urljoin(data['host'], path)

        try:

            url_data = load_report('url', config, id=data['site_id'], url=url)

            if url_data and time_col in url_data:
                last_check = datetime.fromisoformat(url_data[time_col]).astimezone(time_zone)
                time_delta = (start_time - last_check).total_seconds()

                if time_delta < 0:
                    # Has been crawled prior to start of process.
                    content = ["{}--/--{}".format(i['type'], i['content']) for i in url_data['content']]
                    issues = [i['name'] for i in url_data['open_issues']]
                    results.append({'url': url, 'path': path, 'issues': issues, 'content': content, 'error': None})
                else:
                    # We have a good response, but the URL has not been crawled yet.
                    # Add to the back of the line.
                    unchecked.append(path)

            else:
                results.append({'url': url, 'path': path, 'issues': [], 'content': [], 'error': "Invalid response from API URL report."})

        except Exception as e:
            results.append({'url': url, 'path': path, 'issues': [], 'content': [], 'error': "Unkown Error: " + str(e)})

    return results


def _compare_diffs(prod, stage, typ, config):

    """Compares diffs based on the given type (issue or content).

    """

    prod_issues, stage_issues = prod[typ], stage[typ]
    diffs = [i for i in stage_issues if i not in prod_issues]

    if typ == "content":
        return [d for d in diffs if not config.contentking.IGNORE_CONTENT[d.split('--/--')[0]]]

    return [d for d in diffs if not config.contentking.IGNORE_ISSUES[d]]


def _compare_results(sample_paths, prod, stage, config):

    """Using the original paths, runs the main review to check for
       differences across both prod and staging results.

    """

    passing = True
    results = []

    for path in sample_paths:

        if path in prod and path in stage:

            content_diffs = _compare_diffs(prod[path], stage[path], "content", config)
            issue_diffs = _compare_diffs(prod[path], stage[path], "issues", config)

            if content_diffs:
                _LOG.info("{} contains content differences.".format(path))
                results.extend([{'path': path, 'url': stage[path]['url'], 'issue': "Difference: " + d} for d in content_diffs])
                passing = False
            if issue_diffs:
                _LOG.info("{} contains issue differences.".format(path))
                results.extend([{'path': path, 'url': stage[path]['url'], 'issue': "Difference: " + d} for d in issue_diffs])
                passing = False

        else:
            _LOG.error("{} not found in both production and staging results.".format(path))
            passing = False


    return passing, results


def _process_results(data):

    """Reviews the returned results for errors.  Logs errors and returns only results with
       valid data.

    """

    result = {}

    for i in data:
        if i['error']:
            _LOG.error("URL: {} encountered an error: {}".format(i['url'], i['error']))
        else:
            result[i.pop('path')] = i

    return result


def run_check_results(sample_paths, start_time, time_zone, config):

    """Monitors paths that were pinged for updated timestamp. Compares allowed differences.

    Parameters
    ----------
    sample_paths: list
        List of paths to check.
    start_time: datetime
        When the difftest was started.
    time_zone: pytz.timezone
        Default timezone to keep times the same.
    """

    batches = [b for b in group_batcher(sample_paths, list, config.contentking.BATCH_SIZE, fill=None)]

    prod_data = {
        'start_time': start_time,
        'time_zone': time_zone,
        'site_id': config.contentking.PROD_SITE_ID,
        'host': config.contentking.PROD_HOST,
        'time_col': config.contentking.TIME_COL
    }

    stage_data = {
        'start_time': start_time,
        'time_zone': time_zone,
        'site_id': config.contentking.STAGE_SITE_ID,
        'host': config.contentking.STAGE_HOST,
        'time_col': config.contentking.TIME_COL
    }

    prod_result = []
    stage_result = []

    # Iterates batches to send to API for data update.
    for batch in tqdm(batches, desc="Checking crawl status of URLs"):

        prod_result.extend(mp_list_map(batch, _check_results, config=config, data=prod_data))
        stage_result.extend(mp_list_map(batch, _check_results, config=config, data=stage_data))

        # TODO: Can adjust this as necessary, pull out to config, or remove.
        time.sleep(config.contentking.BATCH_WAIT)


    # Review for Errors and process into dictionary:
    prod_result = _process_results(prod_result)
    stage_result = _process_results(stage_result)

    passing, results = _compare_results(sample_paths, prod_result, stage_result, config)

    if not passing:
        _LOG.error("Check completed with errors.  Please review")

    return passing, results
