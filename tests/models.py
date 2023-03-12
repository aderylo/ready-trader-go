from dataclasses import dataclass
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
        

