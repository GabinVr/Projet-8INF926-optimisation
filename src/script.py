#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import subprocess

csv_path = "data/DataProjet2026.csv"
max_cases = 100

Path("data2").mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path, nrows=max_cases)
qtotal_col = df.columns[1]
hamont_col = df.columns[4]

for i, row in df.iterrows():
    Qtotal = row[qtotal_col]
    h_amont = row[hamont_col]

    output_filename = f"data2/bb_{i}.txt"

    command = [
        "julia",
        "partie2.jl",
        "single",
        str(Qtotal),
        str(h_amont),
    ]

    print(f"Running command: {' '.join(command)}")

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True
    )

    julia_output = result.stdout.strip()

    with open(output_filename, "w") as f:
        f.write(julia_output)
