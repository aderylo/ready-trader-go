import pytest
import pandas as pd
import pathlib
from util import create_test_env, setup_test_env, run_test, winner

MAX_TEAMS = 8
TEAM_NAME = "PurpleHaze"


# def test_basic():
#     prefix = "tests/configs/basic/"
#     hdu_port = 8000
#     trader_bins = [
#         "autotrader",
#         "default1",
#     ]
#     traders = [prefix + trader for trader in trader_bins]
#     command = [
#         "python3",
#         "rtg.py",
#         "run",
#         f"--port={hdu_port}",
#         f"--config={prefix}exchange.json",
#     ] + traders
#     print(command)
#     subprocess.run(["bash tests/scripts/update.sh basic"], shell=True)
#     try:
#         subprocess.run(command, timeout=120)
#     except subprocess.TimeoutExpired:
#         pass

#     df = pd.read_csv("tests/logs/basic/score_board.csv")
#     tail = df.tail(len(traders))
#     tail = tail.sort_values(by="ProfitOrLoss", ascending=False)

#     assert tail.iloc[0]["Team"] == "PrupleHaze"


@pytest.mark.parametrize(
    "market_data",
    [
        pathlib.Path("data/market_data1.csv"),
        pathlib.Path("data/market_data2.csv"),
        pathlib.Path("data/market_data3.csv"),
        pathlib.Path("data/market_data4.csv"),
    ],
)
def test_single(market_data: pathlib.Path):
    test_env_path = create_test_env("tests/configs/single", "single", market_data.stem)
    score_board_path = test_env_path / "score_board.csv"

    setup_test_env(test_env_path, market_data)
    run_test(test_env_path)

    assert winner(score_board_path) == TEAM_NAME


def test_lol():
    import time

    time.sleep(5)
    assert True == True
