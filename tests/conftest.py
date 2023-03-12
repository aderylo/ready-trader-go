import pytest


def pytest_addoption(parser):
    parser.addoption("--hdu", action="store", default=False, type=bool)
    parser.addoption("--speed", action="store", default=10.0, type=float)


@pytest.fixture(scope="session")
def run_with_hdu(pytestconfig):
    return pytestconfig.getoption("hdu")


@pytest.fixture(scope="session")
def speed(pytestconfig):
    return pytestconfig.getoption("speed")
