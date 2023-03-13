from dataclasses import dataclass, field
import pathlib
import json
import shutil


@dataclass
class Trader:
    name: str
    binary: str
    team_name: str

    def save_to_json(self, directory: pathlib.Path) -> None:
        path = directory / f"{self.name}.json"
        config = {
            "Execution": {"Host": "127.0.0.1", "Port": 12343},
            "Information": {"Type": "mmap", "Name": "info.dat"},
            "TeamName": self.team_name,
            "Secret": "secret",
        }

        with path.open("w") as f:
            json.dump(config, f, indent=2, separators=(",", ": "))

    def copy_binary(self, directory: pathlib.Path) -> None:
        path_to_binary = pathlib.Path(f"build/{self.binary}")
        new_path_to_binary = directory / self.name
        shutil.copy(path_to_binary, new_path_to_binary)


@dataclass
class _Engine:
    MarketDataFile: str = "data/market_data1.csv"
    MarketEventInterval: float = 0.05
    MarketOpenDelay: float = 5.0
    MatchEventsFile: str = "match_events.csv"
    ScoreBoardFile: str = "score_board.csv"
    Speed: float = 1.0
    TickInterval: float = 0.25


@dataclass
class _Execution:
    Host: str = "127.0.0.1"
    Port: int = 45359


@dataclass
class _Fees:
    Maker: float = -0.0001
    Taker: float = 0.0002


@dataclass
class _Hud:
    Host: str = "127.0.0.1"
    Port: int = 43831


@dataclass
class _Information:
    Type: str = "mmap"
    Name: str = "info.dat"


@dataclass
class _Instrument:
    EtfClamp: float = 0.002
    TickSize: float = 1.0


@dataclass
class _Limits:
    ActiveOrderCountLimit: int = 10
    ActiveVolumeLimit: int = 200
    MessageFrequencyInterval: float = 1.0
    MessageFrequencyLimit: int = 50
    PositionLimit: int = 100


@dataclass
class _Traders:
    PurpleHaze: str = "secret"
    TraderTwo: str = "secret"


@dataclass
class _Exchange:
    Engine: _Engine = field(default_factory=_Engine)
    Execution: _Execution = field(default_factory=_Execution)
    Fees: _Fees = field(default_factory=_Fees)
    Hud: _Hud = field(default_factory=_Hud)
    Information: _Information = field(default_factory=_Information)
    Instrument: _Instrument = field(default_factory=_Instrument)
    Limits: _Limits = field(default_factory=_Limits)
    Traders: list[Trader] = field(default_factory=list)

    def get_teams_dict(self):
        teams = {}
        for trader in self.Traders:
            teams[trader.team_name] = "secret"

        return teams

    def create_config(self):
        config = {}
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                config[key] = self.get_teams_dict()
            else:
                config[key] = value.__dict__

        return config

    def save_config(self, directory: pathlib.Path) -> None:
        path = directory / "exchange.json"
        with path.open("w") as f:
            json.dump(self.create_config(), f, indent=2, separators=(",", ": "))
