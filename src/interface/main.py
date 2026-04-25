import tkinter as tk
from tkinter import StringVar, ttk
from typing import Any, Type
import subprocess
from multiprocessing import Pool
import re

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


### Root
root = tk.Tk()
root.attributes('-type', 'dialog')
root.geometry("1200x1300")

frm = ttk.Frame(root, padding=20)
frm.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

for col in range(6):
    frm.grid_columnconfigure(col, weight=1)


DEFAULT_QTOTAL = "578.01"
DEFAULT_H_AMONT = "138.90"
DEFAULT_Q_MIN = "0"
DEFAULT_Q_MAX = "160"


### Wrappers
def validate(tp: Type):
    def wrapped(value: Any) -> bool:
        try:
            # return not value or tp(value) >= 0
            return not value or tp(value) >= 0
        except:
            return False
    return wrapped

def placeholder(target: ttk.Entry, default_value: str):
    def on_focus_out(_):
        if target.get() == "":
            target.insert(0, default_value)
    return on_focus_out


float_validator = root.register(validate(float))
int_validator = root.register(validate(int))


### First row
params_label = ttk.Label(frm, text="Global Parameters")
params_label.grid(column=0, row=0, columnspan=6, sticky="w", pady=(0, 4))

ttk.Separator(frm, orient="horizontal").grid(
    column=0, row=1, columnspan=6, sticky="ew", pady=(0, 8)
)

ttk.Label(frm, text="Qtotal").grid(column=0, row=2, sticky="e", padx=(0, 6), pady=4)
qtotal = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=10)
qtotal.grid(column=1, row=2, sticky="w", pady=4)
qtotal.insert(-1, DEFAULT_QTOTAL)
qtotal.bind("<FocusOut>", placeholder(qtotal, DEFAULT_QTOTAL))

ttk.Label(frm, text="h_amont").grid(column=0, row=3, sticky="e", padx=(0, 6), pady=4)
h_amont = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=10)
h_amont.grid(column=1, row=3, sticky="w", pady=4)
h_amont.insert(-1, DEFAULT_H_AMONT)
h_amont.bind("<FocusOut>", placeholder(h_amont, DEFAULT_H_AMONT))


### Second row
ttk.Separator(frm, orient="horizontal").grid(
    column=0, row=4, columnspan=6, sticky="ew", pady=(12, 8)
)
flow_label = ttk.Label(frm, text="Flow Ranges per Channel")
flow_label.grid(column=0, row=5, columnspan=6, sticky="w", pady=(0, 4))

# Column headers for channels
for i in range(1, 6):
    ttk.Label(frm, text=f"Ch. {i}").grid(
        column=i, row=6, sticky="ew", padx=4, pady=(0, 2)
    )

ttk.Label(frm, text="Débit min").grid(column=0, row=7, sticky="e", padx=(0, 6), pady=4)
ttk.Label(frm, text="Débit max").grid(column=0, row=8, sticky="e", padx=(0, 6), pady=4)

qX_min = [
    ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=7)
    for _ in range(1, 6)
]
for idx, itm in enumerate(qX_min):
    itm.grid(column=idx + 1, row=7, sticky="ew", padx=4, pady=4)
    itm.insert(-1, "0")
    itm.bind("<FocusOut>", placeholder(itm, DEFAULT_Q_MIN))

qX_max = [
    ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=7)
    for _ in range(1, 6)
]
for idx, itm in enumerate(qX_max):
    itm.grid(column=idx + 1, row=8, sticky="ew", padx=4, pady=4)
    itm.insert(-1, "160")
    itm.bind("<FocusOut>", placeholder(itm, DEFAULT_Q_MAX))


### Compute logic
def compute_single():
    result = subprocess.run(
        ["julia", "main.jl", qtotal.get(), h_amont.get(), *[x.get() for x in qX_min], *[x.get() for x in qX_max]],
        capture_output=True,
        text=True
    )
    output.set(result.stdout)



def cpt(idx: int):
    qtotal_excel = [578.01,580.30,578.55,580.23,574.05,576.18,579.88,573.77,567.09,567.58,569.64,568.90,571.02,568.59,570.66,570.66,565.88,570.40,564.14,567.42,567.43,]
    h_amont_excel = [137.90,137.89,137.89,137.89,137.89,137.89,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,137.88,]

    return subprocess.run(
        ["julia", "main.jl", str(qtotal_excel[idx]), str(h_amont_excel[idx]), *[x.get() for x in qX_min], *[x.get() for x in qX_max]],
        capture_output=True,
        text=True
    ).stdout


def compute_20_first():
    excel_default = [179.18,179.5,179.12,179.51,178.31,178.73,179.25,178.04999999999998,176.70999999999998,176.70999999999998,177.16,176.93,177.62,176.94,177.39000000000001,177.39000000000001,176.24,177.4,176.54999999999998,176.71999999999997]
    q1 = [158.00,160.00,158.00,160.00,154.00,156.00,159.00,153.00,147.00,147.00,149.00,148.00,151.00,148.00,150.00,150.00,146.00,150.00,0.00,147.00]
    q2 = [141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00,141.00]
    q3 = [0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,142.00,0.00]
    q4 = [140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,139.00,140.00,141.00,140.00]
    q5 = [140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,140.00,141.00,140.00]

    with Pool() as p:
        result = p.map(cpt, range(20))

    power_pattern = re.compile(r"Puissance totale predite: (\d+\.?\d*) MW")
    q1_pattern = re.compile(r"Turbine 1: (\d+\.?\d*) m3/s")
    q2_pattern = re.compile(r"Turbine 2: (\d+\.?\d*) m3/s")
    q3_pattern = re.compile(r"Turbine 3: (\d+\.?\d*) m3/s")
    q4_pattern = re.compile(r"Turbine 4: (\d+\.?\d*) m3/s")
    q5_pattern = re.compile(r"Turbine 5: (\d+\.?\d*) m3/s")

    q1_ = [float(q1_pattern.search(i).group(1)) for i in result] # pyright: ignore
    q2_ = [float(q2_pattern.search(i).group(1)) for i in result] # pyright: ignore
    q3_ = [float(q3_pattern.search(i).group(1)) for i in result] # pyright: ignore
    q4_ = [float(q4_pattern.search(i).group(1)) for i in result] # pyright: ignore
    q5_ = [float(q5_pattern.search(i).group(1)) for i in result] # pyright: ignore
    result = [float(power_pattern.search(i).group(1)) for i in result] # pyright: ignore

    fig = Figure(figsize=(4, 8))
    fig.subplots_adjust(hspace=0.6)
    ax = fig.add_subplot(3, 2, 1)
    ax2 = fig.add_subplot(3, 2, 2)
    ax3 = fig.add_subplot(3, 2, 3)
    ax4 = fig.add_subplot(3, 2, 4)
    ax5 = fig.add_subplot(3, 2, 5)
    ax6 = fig.add_subplot(3, 2, 6)

    ax.set_title(f'Puissance produite')
    ax.plot(excel_default, label='Excel (sans restrictions)', marker='o', linestyle='-', color='blue', markersize=4)
    ax.plot(result, label='Excel (avec restrictions)', marker='x', linestyle='-', color='red', markersize=4)

    ax.set_xlabel('Ligne')
    ax.set_ylabel('Puissance (MW)')
    ax.set_xticks(range(0, len(excel_default), 2))

    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)


    for i in [(ax2, q1, q1_, 'Q1'), (ax3, q2, q2_, 'Q2'), (ax4, q3, q3_, 'Q3'), (ax5, q4, q4_, 'Q4'), (ax6, q5, q5_, 'Q5')]:
        i[0].set_title(f'Débit {i[3]}')
        i[0].plot(i[1], linestyle='-', color='blue')
        i[0].plot(i[2], linestyle='-', color='red')

        i[0].set_xlabel('Ligne')
        i[0].set_ylabel('Débit')
        i[0].set_xticks(range(0, len(excel_default), 2))

        i[0].grid(True, linestyle='--', alpha=0.6)


    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(column=0, row=12, columnspan=6, sticky="nsew", pady=(12, 12), padx=(12, 12))




### Third row
ttk.Separator(frm, orient="horizontal").grid(
    column=0, row=9, columnspan=6, sticky="ew", pady=(12, 8)
)

btn_frame = ttk.Frame(frm)
btn_frame.grid(column=0, row=10, columnspan=6, sticky="ew")
btn_frame.grid_columnconfigure(0, weight=1)
btn_frame.grid_columnconfigure(1, weight=1)
btn_frame.grid_columnconfigure(2, weight=1)

ttk.Button(btn_frame, text="Compute", command=compute_single).grid(
    column=0, row=0, sticky="ew", padx=4
)
ttk.Button(btn_frame, text="Compute from Excel", command=compute_20_first).grid(
    column=1, row=0, sticky="ew", padx=4
)
ttk.Button(btn_frame, text="Quit", command=root.destroy).grid(
    column=2, row=0, sticky="ew", padx=4
)


### Last row
ttk.Separator(frm, orient="horizontal").grid(
    column=0, row=11, columnspan=6, sticky="ew", pady=(12, 8)
)

output = StringVar(root, "No compute yet")
ttk.Label(frm, textvariable=output, wraplength=560, justify="left").grid(
    column=0, row=12, columnspan=6, sticky="ew", pady=(0, 8)
)


root.mainloop()
