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

from seodeploy.lib.logging import get_logger
from seodeploy.lib.helpers import group_batcher, mp_list_map, list_to_dict
from .exceptions import ContentKingAPIError

_LOG = get_logger(__name__)


def load_report(report, config, **data):
    """Reporting class for ContentKing.

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

    """

    def api_reports(report, data=None):
        """Report repository for ContentKing API"""

        reports = {
            "websites": "websites",
            "alerts": "websites/{id}/alerts",
            "issues": "websites/{id}/issues",
            "segments": "websites/{id}/segments",
            "statistics": "websites/{id}/statistics/website",
            "statistics:segment": "websites/{id}/statistics/segment:{segment_id}",
            "url": "websites/{id}/pages?url={url}",
            "pages": "websites/{id}/pages/list",
        }
        return reports.get(report, "404").format(**data)

    def get_report(report, config, data, query_string=None):
        """Requests report from ContenKing API"""

        api_url = urljoin(config.contentking.ENDPOINT, api_reports(report, data))

        headers = {
            "User-Agent": "Python CI/CD Testing",
            "Authorization": "token {}".format(config.contentking.REPORT_API_KEY),
            "Content-Type": "application/json",
        }

        tries = 3
        for i in range(tries):

            try:
                response = requests.get(
                    api_url,
                    params=query_string,
                    headers=headers,
                    timeout=config.contentking.API_TIMEOUT,
                    verify=False,
                )

                # Raise HTTPError if not 20X
                response.raise_for_status()
                break

            except requests.exceptions.Timeout as err:
                _LOG.error(str(err))
                time.sleep((i + 1) * 10)

            # Not sure why Requests throws this instead of `Timeout` for timeouts.
            except requests.exceptions.ConnectionError as err:
                _LOG.error(str(err))
                time.sleep((i + 1) * 10)

            except requests.exceptions.HTTPError as err:
                api_message = response.json()["message"]
                _LOG.error("{} ({})".format(str(err), api_message))
                break

            # If it is an unknown error, let's break and raise exception.
            except Exception as err:  # noqa
                _LOG.error("Unspecified ContentKing Error:" + str(err))
                raise ContentKingAPIError(str(err))

        if response and response.status_code == 200:
            return response.json()

        return None

    def get_paged_report(report, config, data):
        """Function for handling paged reports from ContentKing API"""

        page = 1
        per_page = data.get("per_page", 100)
        while True:
            query_string = {"page": page, "per_page": per_page}

            result = get_report(report, config, data, query_string=query_string)

            if result:
                urls = result["urls"]
                yield urls

                time.sleep(2)  # Arbitrarily selected wait.

                if len(urls) < per_page:
                    break

                page += 1

            else:
                yield []
                break

    paged_reports = ["pages"]

    if report in paged_reports:
        return get_paged_report(report, config, data)

    return get_report(report, config, data)


def _notify_change(url, config):
    """Pings ContentKing CMS API about URL changes"""

    api_url = urljoin(config.contentking.ENDPOINT, "check_url")

    headers = {
        "User-Agent": "Python CI/CD Testing",
        "Authorization": "token {}".format(config.contentking.CMS_API_KEY),
        "Content-Type": "application/json",
    }

    data = json.dumps({"url": url})

    tries = 3
    for i in range(tries):

        try:
            response = requests.post(
                api_url,
                data=data,
                headers=headers,
                timeout=config.contentking.API_TIMEOUT,
                verify=False,
            )
            # Raise HTTPError if not 20X
            response.raise_for_status()
            break

        except requests.exceptions.Timeout as err:
            _LOG.error(str(err))
            time.sleep((i + 1) * 10)

        # Not sure why Requests throws this instead of `Timeout` for timeouts.
        except requests.exceptions.ConnectionError as err:
            _LOG.error(str(err))
            time.sleep((i + 1) * 10)

        except requests.exceptions.HTTPError as err:
            api_message = response.json()["message"]
            _LOG.error("{} ({})".format(str(err), api_message))
            break

        # Just want to catch any other errors to the log, so we can add in here.
        except Exception as err:  # noqa
            _LOG.error("Unspecified Error:" + str(err))
            break

    if response and response.status_code == 200:
        return response.json()

    return None


def ping_prod_paths(paths, config):
    """Converts all production paths to URLs and pings ContentKing"""

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
    """Converts all staging paths to URLs and pings ContentKing"""

    results = {}
    for path in paths:
        url = urljoin(config.contentking.STAGE_HOST, path)
        result = _notify_change(url, config)

        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results


def has_ping_errors(name, sample_paths, ping_results):
    """Checks ping results for errors"""

    sent_total = len(sample_paths)

    sent_percent = round(
        (len([k for k, v in ping_results.items() if v == "ok"]) / sent_total) * 100, 2,
    )
    _LOG.info("{}% of {} URLs successfully sent.".format(sent_percent, name))

    if sent_percent < 100:
        sent_errors = [k for k, v in ping_results.items() if v == "error"]
        for i in sent_errors:
            _LOG.error("{} URL Ping Error: {}".format(name, i))

        return True

    return False


def run_path_pings(sample_paths, config):

    """Pings ContentKing with Paths across both staging and production websites.

    Parameters
    ----------
    sample_paths: <list>
        List of paths to check.
    config: <class>
        Module configuration class.
    """

    # Ping Content King for Production and Staging URLs
    batches = group_batcher(
        sample_paths, list, config.contentking.BATCH_SIZE, fill=None
    )
    prod_ping_results = {}
    stage_ping_results = {}

    for batch in tqdm(batches, desc="Pinging API Production and Staging URLs"):
        prod_ping_results.update(ping_prod_paths(batch, config))
        stage_ping_results.update(ping_stage_paths(batch, config))

    # Check results
    if prod_ping_results:
        prod_sent_errors = has_ping_errors(
            "Production", sample_paths, prod_ping_results
        )
    else:
        _LOG.error("No results from Production pings.")

    if stage_ping_results:
        stage_sent_errors = has_ping_errors("Staging", sample_paths, stage_ping_results)
    else:
        _LOG.error("No results from Staging pings.")

    if prod_sent_errors or stage_sent_errors:
        raise ContentKingAPIError(
            "There were issues sending the production and/or staging URLs to ContentKing. "
            "Please check the error log."
        )

    return True


def _check_results(paths, config=None, data=None):

    """Loads path data from ContentKing and returns cleaned data report.

       Checks to see if the latest crawl timestamp is more recent than when this process started.

    """

    unchecked = paths.copy()
    results = []

    while unchecked:

        # Grab the first
        path = unchecked.pop(0)

        url = urljoin(data["host"], path)

        try:

            url_data = load_report("url", config, id=data["site_id"], url=url)

            fmt = {
                "path": path,
                "issues": [],
                "content": [],
                "schema": [],
                "error": None,
            }

            if url_data and data["time_col"] in url_data:
                last_check = datetime.fromisoformat(
                    url_data[data["time_col"]]
                ).astimezone(data["time_zone"])
                time_delta = (data["start_time"] - last_check).total_seconds()

                if time_delta < 0:

                    # Has been crawled prior to start of process.
                    fmt["content"] = [
                        {"element": i["type"], "content": i["content"]}
                        for i in url_data["content"]
                    ]
                    fmt["issues"] = [i["name"] for i in url_data["open_issues"]]
                    fmt["schema"] = url_data["schema_org"]
                    results.append(fmt)

                else:
                    # We have a good response, but the URL has not been crawled yet.
                    # Add to the back of the line.
                    unchecked.append(path)

            else:
                fmt["error"] = "Invalid response from API URL report."
                results.append(fmt)

        except Exception as e:  # noqa
            fmt["error"] = "Unkown Error: " + str(e)
            results.append(fmt)

    return results


def _process_results(sample_paths, prod_result, stage_result):

    """Reviews the returned results for errors. Build single
       result dictionary in the format:

       {'<path>':{'prod': <prod url data>, 'stage': <stage url data>, 'error': error},
       ...
       }


    """

    result = {}

    prod_data = list_to_dict(prod_result, "path")
    stage_data = list_to_dict(stage_result, "path")

    for path in sample_paths:
        error = (
            prod_data[path]["error"] or stage_data[path]["error"]
        )  # TODO: This is not correct.
        result[path] = {
            "prod": prod_data[path]["page_data"],
            "stage": stage_data[path]["page_data"],
            "error": error,
        }

    return result


def run_check_results(sample_paths, start_time, time_zone, config):

    """Monitors paths that were pinged for updated timestamp. Compares allowed differences.

    Parameters
    ----------
    sample_paths: <list>
        List of paths to check.
    start_time: <datetime>
        When the difftest was started.
    time_zone: <pytz.timezone>
        Default timezone to keep times the same.
    config: <class>
        Module configuration class.
    """

    batches = group_batcher(
        sample_paths, list, config.contentking.BATCH_SIZE, fill=None
    )

    prod_data = {
        "start_time": start_time,
        "time_zone": time_zone,
        "site_id": config.contentking.PROD_SITE_ID,
        "host": config.contentking.PROD_HOST,
        "time_col": config.contentking.TIME_COL,
    }

    stage_data = {
        "start_time": start_time,
        "time_zone": time_zone,
        "site_id": config.contentking.STAGE_SITE_ID,
        "host": config.contentking.STAGE_HOST,
        "time_col": config.contentking.TIME_COL,
    }

    prod_result = []
    stage_result = []

    # Iterates batches to send to API for data update.
    for batch in tqdm(batches, desc="Checking crawl status of URLs"):

        prod_result.extend(
            mp_list_map(batch, _check_results, config=config, data=prod_data)
        )
        stage_result.extend(
            mp_list_map(batch, _check_results, config=config, data=stage_data)
        )

        # TODO: Can adjust this as necessary, pull out to config, or remove.
        time.sleep(config.contentking.BATCH_WAIT)

    # Review for Errors and process into dictionary
    page_data = _process_results(sample_paths, prod_result, stage_result)

    return page_data
