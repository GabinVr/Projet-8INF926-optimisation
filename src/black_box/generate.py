#!/usr/bin/env python3

import pandas as pd
import os
from pathlib import Path

def generate_param_file(case_id, Qtotal, h_amont, output_dir):
    
    param_file = os.path.join(output_dir, f"param_case_{case_id}.txt")
    
    with open(param_file, 'w') as f:

        f.write("DIMENSION 7\n")

        f.write("BB_EXE \"../bb.jl\"\n")
        f.write("BB_OUTPUT_TYPE OBJ EB\n")

        f.write(f"X0 ( 120 120 120 120 120 - - )\n")
        f.write("GRANULARITY ( 5 5 5 5 5 - - )\n")

        f.write(f"LOWER_BOUND ( 0 0 0 0 0 - - )\n")
        f.write(f"UPPER_BOUND ( 160 160 160 160 160 - - )\n")
        f.write(f"FIXED_VARIABLE ( - - - - - {Qtotal:.2f} {h_amont:.2f} )\n")

        f.write("MAX_BB_EVAL 50\n")

        f.write("INITIAL_FRAME_SIZE (160 160 160 160 160 - -)\n")

        f.write("NB_THREADS_PARALLEL_EVAL 12\n") # please eat my cpu

        f.write("DISPLAY_DEGREE 2\n")
        f.write("DISPLAY_ALL_EVAL true\n")
        f.write("DISPLAY_STATS BBE ( SOL ) OBJ CONS_H\n")
        f.write(f"STATS_FILE stats_case_{case_id}.txt BBE ( SOL ) OBJ\n")

        f.write(f"SOLUTION_FILE params/solution_case_{case_id}.txt\n")
    
    return param_file



csv_path = "../data/DataProjet2026.csv"
output_dir = "params"
max_cases=100

Path(output_dir).mkdir(parents=True, exist_ok=True)
df = pd.read_csv(csv_path, nrows=max_cases)

param_files = []

qtotal_col = df.columns[1]
hamont_col = df.columns[4]

for i, row in df.iterrows():
    Qtotal = row[qtotal_col]
    h_amont = row[hamont_col]
    
    param_file = generate_param_file(i+1, Qtotal, h_amont, output_dir)
    param_files.append(param_file)
    
    print(f"Cas {i+1} généré : Qtotal={Qtotal:.2f}, h_amont={h_amont:.2f}")

