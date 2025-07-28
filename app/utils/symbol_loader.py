import pandas as pd
from pathlib import Path

def get_kospi100_symbols() -> list[str]:
    csv_path = Path(__file__).resolve().parent.parent / "resources" / "kospi100.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")
    return df['Symbol'].dropna().tolist()