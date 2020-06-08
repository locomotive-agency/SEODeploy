"""Test Cases for Config Module"""

from unittest.mock import Mock
import pytest

from seodeploy.lib import config
from seodeploy.lib.exceptions import ModuleNotImplemented


@pytest.fixture
def config_class():
    """Returns a Wallet instance with a zero balance"""

    def _config(**kwargs):
        return config.Config(**kwargs)

    return _config


def test_config(config_class):
    cfiles = ["tests/files/seotesting_config.yaml"]
    config = config_class(module=None, mdirs=None, cfiles=cfiles)
    assert config.seotesting_name == "SEODeploy-Test"
    assert config.modules == ["contentking", "example_module", "headless"]


def test_config_module(config_class):
    cfiles = ["tests/files/seotesting_config.yaml"]
    config = config_class(module="headless", mdirs=None, cfiles=cfiles)
    assert config.headless.pyppeteer_chromium_revision == 769582
    assert config.modules == ["contentking", "example_module", "headless"]


def test_config_wrong_module(config_class):
    cfiles = ["tests/files/seotesting_config.yaml"]
    with pytest.raises(ModuleNotImplemented):
        config = config_class(module="doesnt_exist", mdirs=None, cfiles=cfiles)
