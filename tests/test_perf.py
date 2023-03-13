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
    traders = [
        Trader(name="autotrader", binary="autotrader", team_name=TEAM_NAME),
    ]
    test_env_path = create_test_env(test_name="single", test_data_name=market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    populate_test_env(test_env_path, traders)
    setup_test_env(test_env_path, market_data, speed, traders)
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

    test_env_path = create_test_env(test_name="basic", test_data_name=market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    populate_test_env(test_env_path, traders)
    setup_test_env(test_env_path, market_data, speed, traders)
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
def test_against_defaults(market_data: pathlib.Path, run_with_hdu, speed):
    traders = [
        Trader(name="autotrader", binary="autotrader", team_name=TEAM_NAME),
        Trader(name="default1", binary="default", team_name="Trader1-default"),
        Trader(name="default2", binary="default", team_name="Trader2-default"),
        Trader(name="default3", binary="default", team_name="Trader3-default"),
        Trader(name="default4", binary="default", team_name="Trader4-default"),
        Trader(name="default5", binary="default", team_name="Trader5-default"),
        Trader(name="default6", binary="default", team_name="Trader6-default"),
        Trader(name="default7", binary="default", team_name="Trader7-default"),
    ]
    test_env_path = create_test_env(
        test_name="seven_defaults", test_data_name=market_data.stem
    )
    score_board_path = test_env_path / "score_board.csv"

    populate_test_env(test_env_path, traders)
    setup_test_env(test_env_path, market_data, speed, traders)
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
    traders = [
        Trader(name="autotrader", binary="autotrader", team_name=TEAM_NAME),
        Trader(name="autotrader1", binary="autotrader", team_name="Trader1-autotrader"),
        Trader(name="autotrader2", binary="autotrader", team_name="Trader2-autotrader"),
        Trader(name="autotrader3", binary="autotrader", team_name="Trader3-autotrader"),
        Trader(name="autotrader4", binary="autotrader", team_name="Trader4-autotrader"),
        Trader(name="autotrader5", binary="autotrader", team_name="Trader5-autotrader"),
        Trader(name="autotrader6", binary="autotrader", team_name="Trader6-autotrader"),
        Trader(name="autotrader7", binary="autotrader", team_name="Trader7-autotrader"),
    ]
    test_env_path = create_test_env("rumble", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    populate_test_env(test_env_path, traders)
    setup_test_env(test_env_path, market_data, speed, traders)
    run_test(test_env_path, run_with_hdu)

    assert winner(score_board_path) == TEAM_NAME
