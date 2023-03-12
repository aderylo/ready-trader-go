import pytest
import pathlib
from util import create_test_env, populate_test_env, setup_test_env, run_test, winner
from models import Trader

TEAM_NAME = "PurpleHaze"


@pytest.mark.parametrize(
    "market_data",
    [
        pathlib.Path("data/market_data1.csv"),
        pathlib.Path("data/market_data2.csv"),
        pathlib.Path("data/market_data3.csv"),
        pathlib.Path("data/market_data4.csv"),
    ],
)
def test_single(market_data: pathlib.Path, run_with_hdu, speed):
    test_env_path = create_test_env("tests/configs/single", "single", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    setup_test_env(test_env_path, market_data, speed)
    run_test(test_env_path, run_with_hdu)

    assert winner(score_board_path) == TEAM_NAME


@pytest.mark.parametrize(
    "market_data",
    [
        pathlib.Path("data/market_data1.csv"),
        pathlib.Path("data/market_data2.csv"),
        pathlib.Path("data/market_data3.csv"),
        pathlib.Path("data/market_data4.csv"),
    ],
)
def test_basic(market_data: pathlib.Path, run_with_hdu, speed):
    traders = [
        Trader(name="autotrader", binary="autotrader", team_name=TEAM_NAME),
        Trader(name="default1", binary="default", team_name="TraderTwo"),
    ]

    test_env_path = create_test_env("tests/configs/basic", "basic", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    populate_test_env(test_env_path, traders)
    setup_test_env(test_env_path, market_data, speed)
    run_test(test_env_path, run_with_hdu)

    assert winner(score_board_path) == TEAM_NAME


@pytest.mark.parametrize(
    "market_data",
    [
        pathlib.Path("data/market_data1.csv"),
        pathlib.Path("data/market_data2.csv"),
        pathlib.Path("data/market_data3.csv"),
        pathlib.Path("data/market_data4.csv"),
    ],
)
def test_eight(market_data: pathlib.Path, run_with_hdu, speed):
    test_env_path = create_test_env("tests/configs/eight", "eight", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    setup_test_env(test_env_path, market_data, speed)
    run_test(test_env_path, run_with_hdu)

    assert winner(score_board_path) == TEAM_NAME


@pytest.mark.parametrize(
    "market_data",
    [
        pathlib.Path("data/market_data1.csv"),
        pathlib.Path("data/market_data2.csv"),
        pathlib.Path("data/market_data3.csv"),
        pathlib.Path("data/market_data4.csv"),
    ],
)
def test_rumble(market_data: pathlib.Path, run_with_hdu, speed):
    test_env_path = create_test_env("tests/configs/rumble", "rumble", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    setup_test_env(test_env_path, market_data, speed)
    run_test(test_env_path, run_with_hdu)

    assert winner(score_board_path) == TEAM_NAME
