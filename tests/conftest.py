import pytest


def pytest_addoption(parser):
    parser.addoption("--hdu", action="store", default=False, type=bool)


@pytest.fixture(scope="session")
def run_with_hdu(pytestconfig):
    return pytestconfig.getoption("hdu")
