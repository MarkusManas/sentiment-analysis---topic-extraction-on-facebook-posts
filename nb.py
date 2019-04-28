import matplotlib.figure
import matplotlib.patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

fig = matplotlib.figure.Figure(figsize=(5,5))
ax = fig.add_subplot(111)
ax.pie([20,30,50]) 
ax.legend(["20","30","50"])
'''
circle=matplotlib.patches.Circle( (0,0), 0.7, color='white')
ax.add_artist(circle)
'''
asd= tk.Tk()
asd.geometry("400x400+100+100")
nb = ttk.Notebook(asd)
frame1 = tk.Frame(nb)

canvas = FigureCanvasTkAgg(fig, master=frame1)
canvas.get_tk_widget().pack()
canvas.draw()

frame1.pack(expand=1, fill=tk.BOTH)
frame2 = tk.Frame(nb)
frame2.pack(expand=1, fill=tk.BOTH)
nb.add(frame1, text="ASDDD")
nb.add(frame2, text="12333")
nb.pack(expand=1, fill=tk.BOTH)
asd.mainloop()