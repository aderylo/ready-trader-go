import subprocess
import pandas as pd
import pathlib
import json
import socket
import shutil
from models import Trader, _Exchange, _Engine, _Information, _Execution, _Hud

MAX_TEAMS = 8
TEST_ENVS_DIR = "tests/envs"


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def load_exchange_config(test_env: pathlib.Path) -> dict:
    config_path = test_env / "exchange.json"
    with config_path.open("r") as config:
        return json.load(config)


def configure_exchange(
    test_env: pathlib.Path,
    data_source: pathlib.Path,
    traders: list[Trader],
    execution_port: int,
    hdu_port: int,
    speed: int = 10.0,
):
    engine = _Engine(
        MarketDataFile=str(data_source),
        MatchEventsFile=str(test_env / "match_events.csv"),
        ScoreBoardFile=str(test_env / "score_board.csv"),
        Speed=speed,
    )
    info = _Information(Name=str(test_env / "info.dat"))
    execution = _Execution(Port=execution_port)
    hud = _Hud(Port=hdu_port)
    exchange = _Exchange(
        Engine=engine, Information=info, Execution=execution, Hud=hud, Traders=traders
    )

    exchange.save_config(test_env)


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


def create_test_env(test_name: str, test_data_name: str) -> pathlib.Path:
    # Generate test env path
    test_env_path = pathlib.Path(f"{TEST_ENVS_DIR}/{test_name}/{test_data_name}")

    if test_env_path.exists():
        shutil.rmtree(test_env_path)

    test_env_path.mkdir(parents=True)

    return test_env_path


def populate_test_env(test_env: pathlib.Path, traders: list[Trader]):
    for trader in traders:
        trader.save_to_json(test_env)
        trader.copy_binary(test_env)


def setup_test_env(
    test_env: pathlib.Path,
    data_source: pathlib.Path,
    speed: float,
    traders: list[Trader],
) -> None:
    execution_port = get_free_port()
    hdu_port = get_free_port()

    configure_exchange(
        test_env=test_env,
        data_source=data_source,
        execution_port=execution_port,
        hdu_port=hdu_port,
        speed=speed,
        traders=traders,
    )
    configure_traders(test_env=test_env)


def run_test(test_env: pathlib.Path, run_with_hdu: bool = False):
    config_path = test_env / "exchange.json"
    config = load_exchange_config(test_env)

    hdu_port = config["Hud"]["Port"]
    traders = [f for f in test_env.glob("*.json") if f.name != "exchange.json"]
    traders = [f.with_suffix("").as_posix() for f in traders]

    command = [
        "python3",
        "rtg.py",
        "run",
        f"--config={str(config_path)}",
    ] + traders

    if run_with_hdu is False:
        command += ["--hdu=0"]
    else:
        command += [f"--port={hdu_port}"]

    try:
        subprocess.run(command, timeout=120)
    except subprocess.TimeoutExpired:
        pass


def winner(score_board_path: pathlib.Path) -> str:
    df = pd.read_csv(str(score_board_path))
    teams = df["Team"].tail(MAX_TEAMS).unique().tolist()
    assert len(teams) != 0

    tail = df.tail(len(teams))
    sorted = tail.sort_values(by="ProfitOrLoss", ascending=False)

    return sorted.iloc[0]["Team"]
