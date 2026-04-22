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
root.geometry("600x800") 

frm = ttk.Frame(root, padding=10)
frm.grid()

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

ttk.Label(frm, text="Qtotal").grid(column=0, row=0, sticky="e")
qtotal = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=7)
qtotal.grid(column=1, row=0)
qtotal.insert(-1, DEFAULT_QTOTAL)
qtotal.bind("<FocusOut>", placeholder(qtotal, DEFAULT_QTOTAL))


ttk.Label(frm, text="h_amont").grid(column=0, row=1, sticky="e")
h_amont = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=7)
h_amont.grid(column=1, row=1)
h_amont.insert(-1, DEFAULT_H_AMONT)
h_amont.bind("<FocusOut>", placeholder(h_amont, DEFAULT_H_AMONT))


### Second row
ttk.Label(frm, text="Débit min").grid(column=0, row=2, sticky="e")
ttk.Label(frm, text="Débit max").grid(column=0, row=3, sticky="e")

qX_min = [ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=7) for _ in range(1, 6)]
for idx, itm in enumerate(qX_min):
    itm.grid(column=idx+1, row=2)
    itm.insert(-1, "0")
    itm.bind("<FocusOut>", placeholder(itm, DEFAULT_Q_MIN))

qX_max = [ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=7) for _ in range(1, 6)]
for idx, itm in enumerate(qX_max):
    itm.grid(column=idx+1, row=3)
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


    with Pool() as p:
        result = p.map(cpt, range(20))

    power_pattern = re.compile(r"Puissance totale predite: (\d+\.?\d*) MW")

    result = [
        float(power_pattern.search(i.split('\n')[-2]).group(1)) # pyright: ignore
        for i in result
    ]

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot()

    ax.plot(excel_default, label='Excel (sans restrictions)', marker='o', linestyle='-', color='blue', markersize=4)
    ax.plot(result, label='Excel (avec restrictions)', marker='x', linestyle='-', color='red', markersize=4)

    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(column=0, row=7)



### Third row

ttk.Button(frm, text="Compute", command=compute_single).grid(column=0, row=4)
ttk.Button(frm, text="Compute from Excel", command=compute_20_first).grid(column=1, row=4)


### Last row
output = StringVar(root, "No compute yet")
ttk.Label(frm, textvariable=output).grid(column=0, row=6, columnspan=6)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=9)


root.mainloop()
