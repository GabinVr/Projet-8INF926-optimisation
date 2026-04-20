import tkinter as tk
from tkinter import StringVar, ttk
from typing import Any, Type
import subprocess



### Root
root = tk.Tk()
root.attributes('-type', 'dialog')
root.geometry("600x400") 

frm = ttk.Frame(root, padding=10)
frm.grid()


### Validators
def validate(tp: Type):
    def wrapped(value: Any) -> bool:
        try:
            # return not value or tp(value) >= 0
            return tp(value) >= 0
        except:
            return False
    return wrapped

float_validator = root.register(validate(float))
int_validator = root.register(validate(int))


### First row

ttk.Label(frm, text="Qtotal").grid(column=0, row=0, sticky="e")
qtotal = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=5)
qtotal.grid(column=1, row=0)
qtotal.insert(-1, "578")

ttk.Label(frm, text="h_amont").grid(column=0, row=1, sticky="e")
h_amont = ttk.Entry(frm, validate="key", validatecommand=(float_validator, "%P"), width=5)
h_amont.grid(column=1, row=1)
h_amont.insert(-1, "137")


### Second row
ttk.Label(frm, text="Débit min").grid(column=0, row=2, sticky="e")
ttk.Label(frm, text="Débit max").grid(column=0, row=3, sticky="e")

qX_min = [ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=5) for _ in range(1, 6)]
for idx, itm in enumerate(qX_min):
    itm.grid(column=idx+1, row=2)
    itm.insert(-1, "0")

qX_max = [ttk.Entry(frm, validate="key", validatecommand=(int_validator, "%P"), width=5) for _ in range(1, 6)]
for idx, itm in enumerate(qX_max):
    itm.grid(column=idx+1, row=3)
    itm.insert(-1, "160")


### Call logic
def compute():
    result = subprocess.run(
        ["julia", "main.jl", qtotal.get(), h_amont.get(), *[x.get() for x in qX_min], *[x.get() for x in qX_max]],
        capture_output=True,
        text=True
    )
    output.set(result.stdout)



ttk.Button(frm, text="Compute", command=compute).grid(column=0, row=4)


output = StringVar(root, "No compute yet")
ttk.Label(frm, textvariable=output).grid(column=0, row=6, columnspan=6)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=9)

root.mainloop()
