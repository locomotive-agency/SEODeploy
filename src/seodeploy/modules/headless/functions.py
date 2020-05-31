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
from tqdm import tqdm

from seodeploy.lib.logging import get_logger
from seodeploy.lib.helpers import group_batcher, mp_list_map, list_to_dict  # noqa

from .render import HeadlessChrome  # noqa
from .exceptions import HeadlessException  # noqa

_LOG = get_logger(__name__)


def _render_paths(paths, config=None, host=None):

    """Renders paths in Google Chrome and returns extracted <dict>.

    """

    chrome = HeadlessChrome(config=config)

    results = []

    for path in paths:

        url = urljoin(host, path)

        result = chrome.render(url)

        if result["error"]:
            results.append({"path": path, "page_data": None, "error": result["error"]})
        else:
            results.append(
                {"path": path, "page_data": result["page_data"], "error": None}
            )

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


def run_render(sample_paths, config):

    """Monitors paths that were pinged for updated timestamp. Compares allowed differences.

    Parameters
    ----------
    sample_paths: <list> List of paths to check.
    config: <class> Configuration class
    """

    batches = group_batcher(sample_paths, list, config.headless.BATCH_SIZE, fill=None)

    prod_result = []
    stage_result = []

    # Iterates batches to send to API for data update.
    for batch in tqdm(batches, desc="Rendering URLs"):

        prod_result.extend(
            mp_list_map(
                batch, _render_paths, config=config, host=config.headless.PROD_HOST
            )
        )
        stage_result.extend(
            mp_list_map(
                batch, _render_paths, config=config, host=config.headless.STAGE_HOST
            )
        )

    # Review for Errors and process into dictionary:
    page_data = _process_results(sample_paths, prod_result, stage_result)

    return page_data
