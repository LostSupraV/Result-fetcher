import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import csv
from app import *
from resultgen import *

# ---------- FUNCTIONS ----------

def switch_mode():
    if mode_var.get() == "roll":
        roll_entry.configure(state="normal")
        branch_box.configure(state="disabled")
    else:
        roll_entry.configure(state="disabled")
        branch_box.configure(state="readonly")


def fetch_results():

    clear_table()

    if mode_var.get() == "branch":
        branch = branch_box.get()
        branch_results = generate_branch_result(branch)
        columns = ("Roll","Name","SPI","CPI","Rank")
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_column(c, False))
            tree.column(col, anchor="center")

        for row in branch_results:
            tree.insert("", "end", values=row)

        info_label.config(text="Branch Results")

    else:
        roll = roll_entry.get()
        s = get_profile(roll)

        info_label.config(
            text=f"Name: {s['name']}   Branch: {s['branch']}   Enrollment: {s['enrollment']}"
        )

        columns = ("Subject","Grade ","Grade Point", "Credits")
        tree["columns"] = columns

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for sub in s["subjects"]:
            tree.insert("", "end", values=sub)

        sgpa_label.config(text=f"SPI: {s['spi']}")
        cpi_label.config(text=f"CPI: {s['cpi']}")


def clear_table():
    for row in tree.get_children():
        tree.delete(row)


def sort_column(col, reverse):

    data = [(tree.set(k, col), k) for k in tree.get_children('')]

    try:
        data.sort(key=lambda t: float(t[0]), reverse=reverse)
    except:
        data.sort(reverse=reverse)

    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_column(col, not reverse))


def export_csv():

    rows = [tree.item(r)["values"] for r in tree.get_children()]

    with open("results.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    status_label.config(text="Exported results.csv")


# ---------- GUI ----------

root = ttk.Window(themename="cosmo")
root.title("Result Portal")
root.geometry("900x550")


title = ttk.Label(root,text="Student Result Portal",font=("Arial",20,"bold"))
title.pack(pady=10)


# Mode selection
mode_frame = ttk.Frame(root)
mode_frame.pack(pady=5)

mode_var = ttk.StringVar(value="roll")

ttk.Radiobutton(
    mode_frame,
    text="Search by Roll",
    variable=mode_var,
    value="roll",
    command=switch_mode
).grid(row=0,column=0,padx=10)

ttk.Radiobutton(
    mode_frame,
    text="Branch Results",
    variable=mode_var,
    value="branch",
    command=switch_mode
).grid(row=0,column=1,padx=10)


# Input section
input_frame = ttk.Frame(root)
input_frame.pack(pady=10)

ttk.Label(input_frame,text="Roll Number").grid(row=0,column=0,padx=5)

roll_entry = ttk.Entry(input_frame,width=20)
roll_entry.grid(row=0,column=1,padx=5)

ttk.Label(input_frame,text="Branch").grid(row=0,column=2,padx=5)

branches = ["CSE","IT","ECE","EE","Mech","Civil","Chemical","Meta","Mining","Biotech","Biomed"]

branch_box = ttk.Combobox(input_frame,values=branches,width=10)
branch_box.grid(row=0,column=3,padx=5)

fetch_btn = ttk.Button(
    input_frame,
    text="Fetch Results",
    bootstyle="success",
    command=fetch_results
)
fetch_btn.grid(row=0,column=4,padx=10)

export_btn = ttk.Button(
    input_frame,
    text="Export CSV",
    bootstyle="info",
    command=export_csv
)
export_btn.grid(row=0,column=5,padx=10)


# Info
info_label = ttk.Label(root,text="")
info_label.pack(pady=5)


# Table
table_frame = ttk.Frame(root)
table_frame.pack(fill="both",expand=True,padx=20,pady=10)

tree = ttk.Treeview(table_frame,show="headings")

tree.pack(side="left",fill="both",expand=True)

scroll = ttk.Scrollbar(table_frame,command=tree.yview)
tree.configure(yscroll=scroll.set)
scroll.pack(side="right",fill="y")


# SGPA CPI
summary_frame = ttk.Frame(root)
summary_frame.pack(pady=5)

sgpa_label = ttk.Label(summary_frame,text="SPI: --",font=("Arial",12))
sgpa_label.grid(row=0,column=0,padx=20)

cpi_label = ttk.Label(summary_frame,text="CPI: --",font=("Arial",12))
cpi_label.grid(row=0,column=1,padx=20)


status_label = ttk.Label(root,text="Ready",anchor="w")
status_label.pack(fill="x",side="bottom")

switch_mode()

root.mainloop()