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

from urllib.parse import urljoin, urlencode
import requests
import json
import time
from tqdm.auto import tqdm

import pytz
from datetime import datetime
import multiprocessing as mp
import numpy as np
import pandas as pd

from .log_helper import get_logger
from .exceptions import *
from .helpers import *

import config

_LOG = get_logger(__name__)


def load_report(report, **data):
    '''
        Description: Receives a report type and names parameters passed to function.  Requests from COntentKing Reporting API.

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

    def api_reports(report, data={}):
        reports={
                'websites'           : 'websites',
                'alerts'             : 'websites/{id}/alerts',
                'issues'             : 'websites/{id}/issues',
                'segments'           : 'websites/{id}/segments',
                'statistics'         : 'websites/{id}/statistics/website',
                'statistics:segment' : 'websites/{id}/statistics/segment:{segment_id}',
                'url'                : 'websites/{id}/pages?url={url}',
                'pages'              : 'websites/{id}/pages/list'
             }
        return reports.get(report,"404").format(**data)

    def get_report(report, data, qs={}):

        api_url = urljoin(config.ENDPOINT, api_reports(report, data))

        headers = {
                    'User-Agent': 'Python CI/CD Testing',
                    'Authorization': 'token {}'.format(config.REPORT_API_KEY),
                    'Content-Type': 'application/json',
                  }

        tries = 3
        for i in range(tries):

            try:
                response = requests.get(api_url, params=qs, headers=headers, timeout=config.API_TIMEOUT, verify=False)
                # Raise HTTPError if not 20X
                response.raise_for_status()
                break

            except requests.exceptions.Timeout as e:
                _LOG.error(str(e))
                time.sleep((i+1)*10)

            # Not sure why Requests throws this instead of `Timeout` for timeouts.
            except requests.exceptions.ConnectionError as e:
                _LOG.error(str(e))
                time.sleep((i+1)*10)

            except requests.exceptions.HTTPError as e:
                api_message = response.json()['message']
                _LOG.error("{} ({})".format(str(e),api_message))
                break

            # If it is an unknown error, let's break and raise exception.
            except Exception as e:
                _LOG.error('Unspecified ContentKing Error:' + str(e))
                raise ContentKingAPIError(str(e))


        if response and response.status_code == 200:
            return response.json()
        else:
            return None


    def get_paged_report(report, data):
        page = 1
        per_page = data.get('per_page', 100)
        while True:
            qs = {'page':page, 'per_page':per_page}

            result = get_report(report, data, qs=qs)

            if result:
                urls = result['urls']
                yield urls

                time.sleep(2) #Arbitrarily selected wait.
                if len(urls) < per_page:
                    break

                page += 1

            else:
                yield []
                break


    paged_reports = ['pages']

    if report in paged_reports:
        return get_paged_report(report, data)
    else:
        return get_report(report, data)




def _notify_change(url):

    api_url = urljoin(config.ENDPOINT, 'check_url')

    headers = {
                'User-Agent': 'Python CI/CD Testing',
                'Authorization': 'token {}'.format(config.CMS_API_KEY),
                'Content-Type': 'application/json',
              }

    data = json.dumps({"url": url})

    tries = 3
    for i in range(tries):

        try:
            response = requests.post(api_url, data=data, headers=headers, timeout=config.API_TIMEOUT, verify=False)
            # Raise HTTPError if not 20X
            response.raise_for_status()
            break

        except requests.exceptions.Timeout as e:
            _LOG.error(str(e))
            time.sleep((i+1)*10)

        # Not sure why Requests throws this instead of `Timeout` for timeouts.
        except requests.exceptions.ConnectionError as e:
            _LOG.error(str(e))
            time.sleep((i+1)*10)

        except requests.exceptions.HTTPError as e:
            api_message = response.json()['message']
            _LOG.error("{} ({})".format(str(e),api_message))
            break

        # Just want to catch any other errors to the log, so we can add in here.
        except Exception as e:
            _LOG.error('Unspecified Error:' + str(e))
            break

    if response and response.status_code == 200:
        return response.json()
    else:
        return None


def ping_prod_paths(paths):

    results = {}
    for path in paths:
        url = urljoin(config.PROD_HOST, path)
        result = _notify_change(url)
        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results


def ping_stage_paths(paths):

    results = {}
    for path in paths:
        url = urljoin(config.STAGE_HOST, path)
        result = _notify_change(url)
        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results



def run_path_pings(sample_paths):

    """Pings ContentKing with Paths across both staging and production websites.

    Parameters
    ----------
    sample_paths: list
        List of paths to check.
    """

    # Ping Content King for Production and Staging URLs
    batches = [b for b in group_batcher(sample_paths, list, config.BATCH_SIZE, fill=None)]
    prod_ping_results = {}
    stage_ping_results = {}

    for batch in tqdm(batches, description="Pinging API Production and Staging URLs"):
        prod_ping_results.update(ping_prod_paths(batch))
        stage_ping_results.update(ping_stage_paths(batch))

    #Check results were pinged correctly.
    sent_total = len(sample_paths)
    prod_sent_errors, stage_sent_errors = True, True

    # Check results
    if prod_ping_results:
        sent_percent    = round( (len([l for l in list(prod_ping_results.keys()) if prod_ping_results[l] == 'ok'])/sent_total) * 100, 2)
        _LOG.INFO('{}% of production URLs successfully sent.'.format(sent_percent))

        if sent_percent < 100:
            prod_sent_errors = [l for l in list(prod_ping_results.keys()) if prod_ping_results[l] != 'ok']
            for e in sent_errors:
                _LOG.ERROR('Production URL Ping Error: {}'.format(e))
        else:
            prod_sent_errors = False
    else:
        _LOG.ERROR('No results from Production pings.')


    if stage_ping_results:
        sent_percent    = round( (len([l for l in list(stage_ping_results.keys()) if stage_ping_results[l] == 'ok'])/sent_total) * 100, 2)
        _LOG.INFO('{}% of production URLs successfully sent.'.format(sent_percent))

        if sent_percent < 100:
            stage_sent_errors = [l for l in list(stage_ping_results.keys()) if stage_ping_results[l] != 'ok']
            for e in sent_errors:
                _LOG.ERROR('Staging URL Ping Error: {}'.format(e))
        else:
            stage_sent_errors = False

    else:
        _LOG.ERROR('No results from Staging pings.')



    if prod_sent_errors or stage_sent_errors:
        raise ContentKingAPIError('There were issues sending the production and/or staging URLs to COntentKing.  Please check the error log.')

    return True




def _check_results(paths, data={}):

    """Loads path data from ContentKing and returns cleaned data report.
       Checks to see if the latest crawl timestamp is more recent than when this process started.

    """

    checked = []
    unchecked = paths

    results = []

    tz = data['tz']

    while unchecked:

        # Grab the first
        path = unchecked.pop(0)

        url  = urljoin(data['host'], path)

        try:

            url_data = load_report('url', id=data['site_id'], url=url)

            if url_data and data['time_col'] in url_data:
                last_check = datetime.fromisoformat(url_data[data['time_col']]).astimezone(tz).isoformat(timespec='seconds'))
                td = (start_time-last_check).total_seconds()
                if td < 0:
                    # Has been crawled prior to start of process.
                    content = [ "{}--/--{}".format(i['type'],i['content']) for i in url_data['content'] ]
                    issues = [ i['name']) for i in url_data['open_issues']]
                    data.append({'url':url, 'path':path, 'issues':issues, 'content': content, 'error': None})
                    checked.append(path)
                else:
                    # We have a good response, but the URL has not been crawled yet.
                    # Add to the back of the line.
                    unchecked.append(path)


            else:
                data.append({'url':url, 'path':path, 'issues':[], 'content': [], 'error': 'Invalid response from API URL report.'})
                checked.append(path)

        except Exception as e:
            data.append({'url':url, 'path':path, 'issues':[], 'content': [], 'error': 'Unkown Error: ' + str(e)})
            checked.append(path)


    return results




def _compare_diffs(prod, stage, typ):

    """Compares diffs based on the given type (issue or content).

    """

    prod_issues, stage_issues = prod[typ], stage[typ]
    diffs = [i for i in stage_issues if i not in prod_issues]

    if typ=="content":
        return [ d for d in diffs if not config.IGNORE_CONTENT[d.split('--/--')[0]] ]

    else:
        return [ d for d in diffs if not config.IGNORE_ISSUES[d] ]




def _compare_results(sample_paths, prod, stage):

    """Using the original paths, runs the main review to check for
       differences across both prod and staging results.

    """

    passing = True
    df = pd.DataFrame()

    for path in sample_paths:

        if path in prod_result and path in stage_result:

            content_diffs = _compare_diffs(prod_result[path], stage_result[path], 'content')
            issue_diffs = _compare_diffs(prod_result[path], stage_result[path], 'issues')

            if content_diffs:
                _LOG.WARNING('{} contains content differences.'.format(path))
                df = df.append([{'path':path, 'url':stage_result['url'], 'diff':d} for d in content_diffs], ignore_index=True)
                passing = False
            if issue_diffs:
                _LOG.WARNING('{} contains issue differences.'.format(path))
                df = df.append([{'path':path, 'url':stage_result['url'], 'diff':d} for d in issue_diffs], ignore_index=True)
                passing = False



        else:
            _LOG.ERROR('{} not found in both production and staging results.'.format(path))
            passing = False



    return passing, df



def _process_results(data):

    """Reviews the returned results for errors.  Logs errors and returns only results with
       valid data.

    """


    result = {}

    for d in data:
        if d['error']:
            _LOG.ERROR('URL: {} encountered and error: {}'.format(d['url'], d['error']))
        else:
            result[d.pop('path')]  = d

    return result




def run_check_results(sample_paths, start_time, tz):

    """Monitors paths that were pinged for updated timestamp. Compares allowed differences.

    Parameters
    ----------
    sample_paths: list
        List of paths to check.
    start_time: datetime
        When the difftest was started.
    tz: pytz.timezone
        Default timezone to keep times the same.


    """


    batches = [b for b in group_batcher(sample_paths, list, config.BATCH_SIZE, fill=None)]


    prod_data = {
            "start_time" : start_time,
            "tz"         : tz,
            "site_id"    : config.PROD_SITE_ID,
            "host"       : config.PROD_HOST,
            "time_col"   : config.TIME_COL
            }

    stage_data = {
            "start_time" : start_time,
            "tz"         : tz,
            "site_id"    : config.STAGE_SITE_ID,
            "host"       : config.STAGE_HOST,
            "time_col"   : config.TIME_COL
            }


    prod_result = []
    stage_result = []

    # Iterates batches to send to API for data update.
    for batch in tqdm(batches, description="Checking crawl status of URLs"):

        prod_result.extend(mp_list_map(batch, _check_results, data=prod_data))
        stage_result.extend(mp_list_map(batch, _check_results, data=stage_data))

        # TODO: Can adjust this as necessary, pull out to config, or remove.
        time.sleep(config.BATCH_WAIT)


    #Review for Errors and process into dictionary:
    prod_result = _process_results(prod_result)
    stage_result = _process_results(stage_result)


    passing, df = _compare_results(sample_paths, prod_result, stage_result)

    if not passing:
        _LOG.ERROR('Check completed with errors.  please review ')
