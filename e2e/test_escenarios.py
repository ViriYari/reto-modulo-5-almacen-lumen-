import pytest
from pytest_bdd import scenarios

pytest_plugins = ["steps.pasos"]

scenarios("features")
