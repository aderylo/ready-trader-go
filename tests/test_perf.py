import pytest
import subprocess
import pandas as pd 

def test_basic():
    prefix = "tests/configs/basic/"
    hdu_port = 8000
    trader_bins = [
        "autotrader",
        "default1",
    ]
    traders = [prefix + trader for trader in trader_bins]
    command = ["python3", "rtg.py", "run",f"--port={hdu_port}", f"--config={prefix}exchange.json"] + traders
    print(command)
    subprocess.run(["bash tests/scripts/update.sh basic"], shell=True)
    try:
        subprocess.run(command, timeout=120)
    except subprocess.TimeoutExpired:
        pass 

    df = pd.read_csv("tests/logs/basic/score_board.csv")
    tail = df.tail(len(traders))
    tail.sort_values(by="ProfitOrLoss", ascending=False, inplace=True)

    assert tail.iloc[0]["Team"] == "PrupleHaze"

def test_single():
    prefix = "tests/configs/single/"
    hdu_port = 12347
    trader_bins = [
        "autotrader",
    ]
    traders = [prefix + trader for trader in trader_bins]
    command = ["python3", "rtg.py", "run",f"--port={hdu_port}", f"--config={prefix}exchange.json"] + traders

    subprocess.run(["bash tests/scripts/update.sh single"], shell=True)
    try:
        subprocess.run(command, timeout=120)
    except subprocess.TimeoutExpired:
        pass 

    df = pd.read_csv("tests/logs/single/score_board.csv")
    tail = df.tail(len(traders))
    tail.sort_values(by="ProfitOrLoss", ascending=False, inplace=True)

    assert tail.iloc[0]["Team"] == "PrupleHaze" 

def test_lol():
    import time
    time.sleep(5)
    assert True == True