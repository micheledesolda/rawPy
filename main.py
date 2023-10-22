import tkinter
from tkinter import filedialog
import customtkinter
from RawPy import rawPy as rp

# functions needed
def open_data():
    # open the velocity step data from an rp file
    # it load using rawPy load_data function
    path_to_data = filedialog.askopenfilename(initialdir="/src/rawPy/main.py")
    with open(path_to_data,"r") as f:
        data = rp.load_data(path_to_data)

# General system settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Starting frame of the application
app = customtkinter.CTk()
app.geometry("720x480")
app.title("RSF Inversion Tool")

## User Interface element
# uploading file
open_button = customtkinter.CTkButton(app, text="Select Data", command=open_data)
open_button.pack(padx=10,pady=10)

# visualize in an interactive plot
# https://github.com/predict-idlab/plotly-resampler
import plotly.graph_objects as go; import numpy as np
from plotly_resampler import register_plotly_resampler

# Call the register function once and all Figures/FigureWidgets will be wrapped
# according to the register_plotly_resampler its `mode` argument
register_plotly_resampler(mode='auto')

x = np.arange(1_000_000)
noisy_sin = (3 + np.sin(x / 200) + np.random.randn(len(x)) / 10) * x / 1_000


# auto mode: when working in an IPython environment, this will automatically be a 
# FigureWidgetResampler else, this will be an FigureResampler
f = go.Figure()
f.add_trace({"y": noisy_sin + 2, "name": "yp2"})
f

# Call the register function once and all Figures/FigureWidgets will be wrapped
# according to the register_plotly_resampler its `mode` argument
register_plotly_resampler(mode='auto')

# run the app
app.mainloop()