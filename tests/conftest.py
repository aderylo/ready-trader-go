import pytest
import pathlib
import subprocess

def pytest_addoption(parser):
    parser.addoption("--hdu", action="store", default=False, type=bool)
    parser.addoption("--speed", action="store", default=10.0, type=float)


@pytest.fixture(scope="session")
def run_with_hdu(pytestconfig):
    return pytestconfig.getoption("hdu")


@pytest.fixture(scope="session")
def speed(pytestconfig):
    return pytestconfig.getoption("speed")

@pytest.fixture(scope="session", autouse=True)
def get_newest_autotrader():
    configs_dir = pathlib.Path("tests/configs")
    for dir in configs_dir.glob("*"):
        command = f"bash tests/scripts/update.sh {dir.name}"
        subprocess.run(command, shell=True)