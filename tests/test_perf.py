import pytest
import subprocess
import pandas as pd
import pathlib
import json
import shutil
import socket
from typing import Optional

MAX_TEAMS = 8
TEAM_NAME = "PurpleHaze"


def configure_exchange(
    test_env: pathlib.Path,
    data_source: pathlib.Path,
    execution_port: int,
    hdu_port: Optional[int],
):
    exchange_config_file = test_env / "exchange.json"
    with exchange_config_file.open("r") as f:
        config = json.load(f)

    match_events_path = test_env / "match_events.csv"
    score_board_path = test_env / "score_board.csv"
    info_path = test_env / "info.dat"

    config["Engine"]["MatchEventsFile"] = str(match_events_path)
    config["Engine"]["ScoreBoardFile"] = str(score_board_path)
    config["Engine"]["MarketDataFile"] = str(data_source)
    config["Information"]["Name"] = str(info_path)
    config["Execution"]["Port"] = execution_port
    if hdu_port is not None:
        config["Hud"]["Port"] = hdu_port

    with exchange_config_file.open("w") as f:
        json.dump(config, f, indent=2, separators=(",", ": "))


def configure_traders(test_env: pathlib.Path):
    exchange_config = load_exchange_config(test_env)
    traders = [f for f in test_env.glob("*.json") if f.name != "exchange.json"]

    execution_port = exchange_config["Execution"]["Port"]

    for trader in traders:
        with trader.open("r") as f:
            config = json.load(f)

        config["Execution"]["Port"] = execution_port

        with trader.open("w") as f:
            json.dump(config, f, indent=2, separators=(",", ": "))


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def create_test_env(
    test_config_dir: pathlib.Path, test_name: str, test_data_name: str
) -> pathlib.Path:
    # Generate test env path
    test_env = pathlib.Path(f"tests/envs/{test_name}/{test_data_name}")
    # Remove the destination directory if it already exists
    if shutil.os.path.exists(test_env):
        shutil.rmtree(test_env)

    shutil.copytree(test_config_dir, test_env)
    return test_env


def setup_test_env(test_env: pathlib.Path, data_source: pathlib.Path) -> None:
    execution_port = get_free_port()
    hdu_port = get_free_port()

    configure_exchange(test_env, data_source, execution_port, hdu_port)
    configure_traders(test_env=test_env)


def load_exchange_config(test_env: pathlib.Path) -> dict:
    config_path = test_env / "exchange.json"
    with config_path.open("r") as config:
        return json.load(config)


def run_test(test_env: pathlib.Path):
    config_path = test_env / "exchange.json"
    config = load_exchange_config(test_env)

    hdu_port = config["Hud"]["Port"]
    traders = [f for f in test_env.glob("*.json") if f.name != "exchange.json"]
    traders = [f.with_suffix("").as_posix() for f in traders]

    command = [
        "python3",
        "rtg.py",
        "run",
        f"--port={hdu_port}",
        f"--config={str(config_path)}",
    ] + traders

    try:
        subprocess.run(command, timeout=120)
    except subprocess.TimeoutExpired:
        return


def winner(score_board_path: pathlib.Path) -> str:
    df = pd.read_csv(str(score_board_path))
    teams = df["Team"].tail(MAX_TEAMS).unique().tolist()
    assert len(teams) != 0

    tail = df.tail(len(teams))
    sorted = tail.sort_values(by="ProfitOrLoss", ascending=False)

    return sorted.iloc[0]["Team"]


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
