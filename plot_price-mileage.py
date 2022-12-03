
import matplotlib.pyplot as plt
import matplotlib.widgets as wdg
from matplotlib.colors import Normalize
from functools import reduce
import pandas as pd
import numpy as np
import requests
import webbrowser
from PIL import Image
from io import BytesIO

MAX_PRC = 6000
MAX_MLG = 300000

# constants
L_offs = 0.05
B_offs = 0.1
W_width = 0.1
S_height = 0.03
Mk_height = 0.5
Md_height = 0.8


# data
data = pd.read_csv('csv/Mercedes-BenzBMWToyotaVolkswagenHyundaiAudiFiatChevroletOpelDaciaPeugeotRenaultSEATCitroenSubaruNissanPorscheFordVolvoLand RoverJaguarJeepMazdaMitsubishiAlfa RomeoLexusSuzukiSkodaKiaDodgeHonda.csv')

# axes
fig, (menu_ax, graph_ax, detail_ax) = plt.subplots(1, 3, figsize=[23,9])
menu_ax.axis('off')
detail_ax.axis('off')

# region make checkboxes
focused_make = None
make_msk = [False] * len(data.index)
make_ax = fig.add_axes((L_offs, 1-Mk_height-B_offs, W_width, Mk_height))
make_labels = list(data.make.unique())
make_check = wdg.CheckButtons(
    ax=make_ax, 
    labels=make_labels
)

def handle_make(label):
    index = make_labels.index(label)
    was_checked = not make_check.get_status()[index]
    global focused_make
    if was_checked and label is not focused_make:   
        make_check.eventson = False
        make_check.set_active(index)
        make_check.eventson = True
        focused_make = label
    else:
        if was_checked:
            focused_make = None
        else:
            focused_make = label

        global make_msk
        make_msk = [(not b if data.at[i, 'make'] == label else b) for i, b in enumerate(make_msk)]
    
    plot_models(focused_make)
    plot_graph()
    

make_check.on_clicked(handle_make)
# endregion

# region model checkboxes
model_msk = [False] * len(data.index)
model_ax = fig.add_axes((2*L_offs+W_width, B_offs, W_width, Md_height))
model_check = None

def plot_models(make):
    model_ax.clear()
    models = sorted(map(str, data[data.make == make].model.unique()))
    global model_check
    model_check = wdg.CheckButtons(
        ax=model_ax, 
        labels=models, 
    )

    def handle_model(label):
        global model_msk
        model_msk = [(not b if data.at[i, 'model'] == label else b) for i, b in enumerate(model_msk)]
        plot_graph()

    model_check.on_clicked(handle_model)
# endregion


# region price slider
price_msk = [True] * len(data.index)
price_ax = fig.add_axes((L_offs, B_offs, W_width, S_height))
price_slide = wdg.Slider(
    ax=price_ax,
    label='price',
    valmin=0,
    valmax=20000,
    valinit=MAX_PRC
)

def handle_price(val):
    # global price_msk
    # price_msk = [p < val for p in data.price]
    graph_ax.set_ylim(None, val)
    plot_graph()

price_slide.on_changed(handle_price)
# endregion

# region mileage slider
mileage_msk = [True] * len(data.index)
mileage_ax = fig.add_axes((L_offs, B_offs + 2*S_height, W_width, S_height))
mileage_slide = wdg.Slider(
    ax=mileage_ax,
    label='mileage',
    valmin=0,
    valmax=500000,
    valinit=MAX_MLG
)

def handle_mileage(val):
    # global mileage_msk
    # mileage_msk = [m < val for m in data.mileage]
    graph_ax.set_xlim(None, val)
    plot_graph()

mileage_slide.on_changed(handle_mileage)
# endregion

# region age slider
age_msk = [True] * len(data.index)
age_ax = fig.add_axes((L_offs, B_offs + 4*S_height, W_width, S_height))
age_slide = wdg.Slider(
    ax=age_ax,
    label='age (yr)',
    valmin=0,
    valmax=25,
    valinit=25
)

def handle_age(val):
    global age_msk
    age_msk = [a < val * 365 for a in data['reg-age']]
    plot_graph()

age_slide.on_changed(handle_age)
# endregion

# region distance slider
distance_msk = [True] * len(data.index)
distance_ax = fig.add_axes((L_offs, B_offs + 6*S_height, W_width, S_height))
distance_slide = wdg.Slider(
    ax=distance_ax,
    label='distance (km)',
    valmin=0,
    valmax=200,
    valinit=200
)

def handle_distance(val):
    global distance_msk
    distance_msk = [d < val for d in data.distance]
    plot_graph()

distance_slide.on_changed(handle_distance)
# endregion


# scatter graph
graph_ax.set(
    xlabel='mileage',
    ylabel='price',
    frame_on=True,
)

def plot_graph(init=False):
    mask = reduce(np.logical_and, (
        make_msk, price_msk, mileage_msk, age_msk, distance_msk, model_msk))

    global graph_data
    graph_data = data[mask]

    global lim_x, lim_y
    lim_x, lim_y = (graph_ax.get_xlim(), graph_ax.get_ylim())

    graph_ax.clear() # TODO: clear scatter instead of axes (scatter.remove)
    global scatter
    scatter = graph_ax.scatter(
        data=graph_data,
        x='mileage',
        y='price',
        s='distance',
        c='reg-age',
        cmap='YlOrRd',
        norm=Normalize(0, 25 * 365)
    )
    graph_ax.grid(visible=True, which='both')
    graph_ax.set(
        xlabel='mileage',
        ylabel='price',
        frame_on=True,
    )
    
    plt.draw()

    if not init:
        graph_ax.set_xlim(lim_x)
        graph_ax.set_ylim(lim_y)
    else:
        graph_ax.set_xlim(0, MAX_MLG)
        graph_ax.set_ylim(0, MAX_PRC)

        plot_models(None)

    


# detail section
detail_index = None
detail_img_ax = fig.add_axes((0.67, 0.45, 0.28, 0.45))
detail_img_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ax = fig.add_axes((0.67, B_offs, 0.28, 0.3))
detail_text_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ar = None

detail_tmpl = '''
    make:       {make}              price:          {price}

    model:      {model}

    year:       {year}              mileage:        {mileage} km


    seller:             {seller-type}                   vehicle type:   {vehicle-type}

    listing age:        {listing-age} days                   feul type:      {fuel-type}

    distance:           {distance:.0f}
'''

def draw_details():
    detail_listing = graph_data.iloc[detail_index]

    # image
    res = requests.get(detail_listing.at['img-url'][:-13])
    img_data = Image.open(BytesIO(res.content))
    global img_ar
    img_ar = detail_img_ax.imshow(img_data)

    # details
    global detail_text_ar
    if detail_text_ar:
        detail_text_ar.remove()

    detail_str = detail_tmpl.format(**detail_listing.to_dict())
    detail_text_ar = fig.text(0.7, 0.12, detail_str)

    plt.draw()

def handle_focus(e):
    did_hit_point, hit_info = scatter.contains(e)
    if did_hit_point:
        global detail_index
        detail_index = hit_info['ind'][0]  # returns index in df (not row label)
        draw_details()
        
    if detail_index is not None and img_ar.contains(e)[0]:
        webbrowser.open('https://www.autoscout24.be/nl/aanbod/' + graph_data.iloc[detail_index].at['guid'])
        
fig.canvas.mpl_connect('button_press_event', handle_focus)

plot_graph(True)
plt.show()