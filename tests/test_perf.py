import pytest
import subprocess
import pandas as pd
import pathlib
import json
import socket
from typing import Optional

MAX_TEAMS = 8
TEAM_NAME = "PurpleHaze"


def configure_exchange(
    exchange_config_file: pathlib.Path,
    data_source: pathlib.Path,
    hdu_port: Optional[int],
):
    with exchange_config_file.open("r") as f:
        config = json.load(f)

    config["Engine"]["MarketDataFile"] = str(data_source)
    if hdu_port is not None:
        config["Hud"]["Port"] = hdu_port

    with exchange_config_file.open("w") as f:
        json.dump(config, f, indent=2, separators=(",", ": "))


def configure_execution_port(config_dir: pathlib.Path, port: int):
    for config_file in config_dir.glob("*.json"):
        with config_file.open("r") as f:
            config = json.load(f)

        config["Execution"]["Port"] = port

        with config_file.open("w") as f:
            json.dump(config, f, indent=2, separators=(",", ": "))


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def performance_test_setup(config_dir: pathlib.Path, data_source: pathlib.Path):
    execution_port = get_free_port()
    hdu_port = get_free_port()
    exchange_config_path = config_dir / "exchange.json"

    configure_execution_port(config_dir, execution_port)
    configure_exchange(exchange_config_path, data_source, hdu_port)


def load_exchange_config(config_path: pathlib.Path) -> dict:
    with config_path.open("r") as config:
        return json.load(config)


def run_test(config_dir: pathlib.Path):
    config_path = config_dir / "exchange.json"
    config = load_exchange_config(config_path)

    hdu_port = config["Hud"]["Port"]
    traders = [f for f in config_dir.glob("*.json") if f.name != "exchange.json"]
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


def test_basic():
    prefix = "tests/configs/basic/"
    hdu_port = 8000
    trader_bins = [
        "autotrader",
        "default1",
    ]
    traders = [prefix + trader for trader in trader_bins]
    command = [
        "python3",
        "rtg.py",
        "run",
        f"--port={hdu_port}",
        f"--config={prefix}exchange.json",
    ] + traders
    print(command)
    subprocess.run(["bash tests/scripts/update.sh basic"], shell=True)
    try:
        subprocess.run(command, timeout=120)
    except subprocess.TimeoutExpired:
        pass

    df = pd.read_csv("tests/logs/basic/score_board.csv")
    tail = df.tail(len(traders))
    tail = tail.sort_values(by="ProfitOrLoss", ascending=False)

    assert tail.iloc[0]["Team"] == "PrupleHaze"


def test_alone():
    config_dir = pathlib.Path("tests/configs/single")

    data = pathlib.Path("data/market_data2.csv")
    performance_test_setup(config_dir, data)
    run_test(config_dir)

    assert winner("tests/logs/single/score_board.csv") == TEAM_NAME


def test_lol():
    import time

    time.sleep(5)
    assert True == True
