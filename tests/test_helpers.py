"""Test Cases for Config Module"""

from unittest.mock import Mock
import pytest

from seodeploy.lib import helpers
from seodeploy.lib.config import Config
from seodeploy.lib.exceptions import ModuleNotImplemented


def test_helpers_group_batcher():
    iterable = [i for i in range(10)]
    batches_list = list(helpers.group_batcher(iterable, list, 5))
    batches_set = list(helpers.group_batcher(iterable, set, 5))
    batches_fill = list(helpers.group_batcher(iterable, list, 4, fill=99))
    batches_fill_none = list(helpers.group_batcher(iterable, list, 4, fill=None))
    assert batches_list == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    assert batches_set == [{0, 1, 2, 3, 4}, {5, 6, 7, 8, 9}]
    assert batches_fill[2][-2:] == [99, 99]
    assert batches_fill_none[2] == [8, 9]


def multi(x, by=0):
    return [i * by for i in x]


def test_helpers_mp_list_map():
    iterable = [i for i in range(10)]
    # TODO: Throws error with Mutli-Processing in Pytest Coverage: See Issue: https://github.com/pytest-dev/pytest-cov/issues/250
    # helpers.CONFIG.MAX_THREADS = 3
    # result_multi = helpers.mp_list_map(iterable, multi, by=10)
    helpers.CONFIG.MAX_THREADS = 1
    result_single = helpers.mp_list_map(iterable, multi, by=10)
    # assert result_multi == [i * 10 for i in iterable]
    assert result_single == [i * 10 for i in iterable]


def test_helpers_url_to_path():
    url = "https://locomotive.agency/path/?query=string#theid"
    assert helpers.url_to_path(url) == "/path/?query=string"


def test_helpers_list_to_dict():
    lst = [{"key": "name1", "value": "data1"}, {"key": "name2", "value": "data2"}]
    assert helpers.list_to_dict(lst, "key") == {
        "name1": {"value": "data1"},
        "name2": {"value": "data2"},
    }


@pytest.fixture
def dotdata():
    return {"a": 1, "b": {"c": 2, "d": 3}}


def test_helpers_dotnot(dotdata):
    dotset = helpers.dot_set(dotdata)
    assert dotset.b.c == 2
    assert helpers.dot_get("b.c", dotdata) == 2
    assert helpers.to_dot(dotdata) == ["a", "b.c", "b.d"]


def test_helpers_process_page_data():

    config = Config(module="headless")

    data1 = [
        {"path": "/path1/", "page_data": ["data1"], "error": None},
        {"path": "/path2/", "page_data": ["data2"], "error": None},
        {"path": "/path3/", "page_data": None, "error": "error3"},
    ]
    data2 = [
        {"path": "/path1/", "page_data": ["data1"], "error": None},
        {"path": "/path2/", "page_data": ["data2"], "error": None},
        {"path": "/path3/", "page_data": None, "error": "error3"},
    ]
    paths = ["/path1/", "/path2/", "/path3/"]

    assert helpers.process_page_data(paths, data1, data2, config.headless) == {
        "/path1/": {"prod": ["data1"], "stage": ["data1"], "error": None},
        "/path2/": {"prod": ["data2"], "stage": ["data2"], "error": None},
        "/path3/": {"prod": None, "stage": None, "error": "error3"},
    }
