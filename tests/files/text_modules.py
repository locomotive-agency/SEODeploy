"""Test Cases for Modules Module"""

from unittest.mock import Mock
import pytest

from seodeploy.lib import module
from seodeploy.lib import config

from seodeploy.lib.exceptions import ModuleNotImplemented


@pytest.fixture
def config_class():
    """Returns a Wallet instance with a zero balance"""

    def _config(**kwargs):
        cfiles = ["tests/files/seotesting_config.yaml"]
        return config.Config(cfiles=cfiles, **kwargs)

    return _config


@pytest.fixture
def module_base_class():
    """Returns a Wallet instance with a zero balance"""

    def _module(**kwargs):
        return module.ModuleBase(**kwargs)

    return _module


@pytest.fixture
def module_config_class():
    """Returns a Wallet instance with a zero balance"""

    def _module(**kwargs):
        return module.ModuleConfig(**kwargs)

    return _module
