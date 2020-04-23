from urllib.parse import urljoin, urlencode
import requests
import json
import time
from tqdm.auto import tqdm

from lib.log_helper import get_logger

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

            # Just want to catch any other errors to the log, so we can add in here.
            except Exception as e:
                _LOG.error('Unspecified Error:' + str(e))
                break

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




def notify_change(url):

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


def process_prod_paths(paths):

    results = {}
    for path in tqdm(paths, desc="Notifying ContentKing to recheck URLs"):
        url = urljoin(config.PROD_HOST, path)
        result = notify_change(url)
        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results


def process_stage_paths(paths):

    results = {}
    for path in tqdm(paths, desc="Notifying ContentKing to recheck URLs"):
        url = urljoin(config.STAGE_HOST, path)
        result = notify_change(url)
        if result:
            results[url] = "ok"
        else:
            results[url] = "error"

    return results
