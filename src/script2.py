#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
import subprocess
import re
from matplotlib import pyplot as plt

power_pattern = re.compile(r"Puissance totale predite: (\d+\.?\d*) MW")

dynamic = []
bb = []

for i in range(0, 100):
    with open(f"data2/bb_{i}.txt") as f:
        l = f.readlines()
        last_line = l[-1].strip()
        match = power_pattern.search(last_line)
        dynamic.append(float(match.group(1)))

for i in range(1, 101):
    with open(f"black_box/params/solution_case_{i}.txt") as f:
        l = f.readlines()[0].split()[7]
        bb.append(-float(l))


print(dynamic)
print(bb)

plt.figure(figsize=(10, 6))

plt.plot(dynamic, label='Dynamic', marker='o', linestyle='-', color='blue', markersize=4)
plt.plot(bb, label='Black box', marker='x', linestyle='--', color='red', markersize=4)

plt.legend()

plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
