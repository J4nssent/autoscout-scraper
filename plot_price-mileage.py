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
from os import listdir

# settings
MAX_PRC = 6000
MAX_MLG = 300000

# constants
WIN_WIDTH, WIN_HEIGHT = 23, 9

V_OFFSET = 0.05
H_OFFSET = 0.1
WDG_WIDTH = 0.1
SLDR_HEIGHT = 0.03
MK_HEIGHT = 0.5
MD_HEIGHT = 0.8

# data
makes = [s.replace('.csv','') for s in listdir('listings')]
listings = pd.DataFrame()

# axes
fig, (menu_ax, graph_ax, detail_ax) = plt.subplots(1, 3, figsize=[WIN_WIDTH, WIN_HEIGHT])
menu_ax.axis('off')
detail_ax.axis('off')

# region make checkboxes
focused_make = None
make_ax = fig.add_axes((V_OFFSET, 1-H_OFFSET-MK_HEIGHT, WDG_WIDTH, MK_HEIGHT))
make_check = wdg.CheckButtons(make_ax, makes)

def handle_make(label):
    label_index = makes.index(label)
    was_checked = not make_check.get_status()[label_index]
    global focused_make
    focused_make = label
    if was_checked:
        if label is not focused_make:   
            print("focus")
            make_check.eventson = False
            make_check.set_active(label_index)
            make_check.eventson = True
        else:
            focused_make = None
    else:
        global listings, model_msk
        model_msk = [False] * len(listings.index)
        if not listings.empty and label in listings.make.unique():
            listings.drop(listings[listings.make == label].index)
        else:
            data = pd.read_csv('listings/' + label + '.csv')
            listings = pd.concat([listings, data], ignore_index=True)
            global age_msk, distance_msk
            age_msk = distance_msk = [True] * len(listings.index)
 
    plot_models(focused_make)
    plot_graph()
    
make_check.on_clicked(handle_make)
# endregion

# region model checkboxes
model_msk = [False] * len(listings.index)
model_ax = fig.add_axes((2*V_OFFSET+WDG_WIDTH, H_OFFSET, WDG_WIDTH, MD_HEIGHT))

def plot_models(make):
    model_ax.clear()
    models = sorted(map(str, listings[listings.make == make].model.unique()))
    model_check = wdg.CheckButtons(
        ax=model_ax, 
        labels=models, 
    )

    def handle_model(label):
        global model_msk
        model_msk = [(not b if listings.at[i, 'model'] == label else b) for i, b in enumerate(model_msk)]
        plot_graph()

    model_check.on_clicked(handle_model)
# endregion

# region sliders
age_msk = distance_msk = [True] * len(listings.index)

def price_cb(val):
    graph_ax.set_ylim(None, val)
    plot_graph()

def mileage_cb(val):
    graph_ax.set_xlim(None, val)
    plot_graph()

def age_cb(val):
    global age_msk
    age_msk = [a < val * 365 for a in listings['reg-age']]
    plot_graph()

def distance_cb(val):
    global distance_msk
    distance_msk = [d < val for d in listings.distance]
    plot_graph()

sliders = [
    {
        label: 'price',
        rect: (V_OFFSET, H_OFFSET, WDG_WIDTH, SLDR_HEIGHT),
        min: 0, max: 20000, init: MAX_PRC
        callback: price_cb
    },{
        label: 'mileage',
        rect: (V_OFFSET, H_OFFSET + 2*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT),
        min: 0, max: 500000, init: MAX_MLG
        callback: mileage_cb
    },{
        label: 'age (yr)',
        rect: (V_OFFSET, H_OFFSET + 4*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT),
        min: 0, max: 25, init: 25
        callback: age_cb
    },{
        label: 'distance (km)',
        rect: (V_OFFSET, H_OFFSET + 6*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT),
        min: 0, max: 25, init: 25
        callback: distance_cb
    },
]

for s in sliders:
    ax = fig.add_axes(s.rect)
    sld = wdg.Slider(
        ax=ax,
        label=s.label,
        valmin=s.min,
        valmax=s.max,
        valinit=s.init
    )
    sld.on_changed(s.callback)
# endregion

# scatter graph
scatter = None

def reset_graph_ax():
    graph_ax.clear()
    graph_ax.grid(
        visible=True, 
        which='both'
    )
    graph_ax.set(
        xlabel='mileage',
        ylabel='price',
        frame_on=True,
    )

def plot_graph(init=False):
    reset_graph_ax()

    if not listings.empty:
        mask = reduce(np.logical_and, (age_msk, distance_msk, model_msk))

        global graph_data
        graph_data = listings[mask]

        print('plot_graph:', graph_data)

        global lim_x, lim_y
        lim_x, lim_y = (graph_ax.get_xlim(), graph_ax.get_ylim())

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

    plt.draw()

    if not init:
        graph_ax.set_xlim(lim_x)
        graph_ax.set_ylim(lim_y)
    else:
        graph_ax.set_xlim(0, MAX_MLG)
        graph_ax.set_ylim(0, MAX_PRC)


# region detail section
detail_index = None
detail_img_ax = fig.add_axes((0.67, 0.45, 0.28, 0.45))
detail_img_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ax = fig.add_axes((0.67, H_OFFSET, 0.28, 0.3))
detail_text_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ar = None

detail_tmpl = '''
    make:       {make}              price:          {price}

    model:      {model}

    year:       {year}              mileage:        {mileage} km


    seller:             {seller-type}                   vehicle type:   {vehicle-type}

    listing age:        {listing-age} days                   fuel type:      {fuel-type}

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
    if scatter is not None:
        did_hit_point, hit_info = scatter.contains(e)
        if did_hit_point:
            global detail_index
            detail_index = hit_info['ind'][0]  # returns index in df (not row label)
            draw_details()
        
    if detail_index is not None and img_ar.contains(e)[0]:
        webbrowser.open('https://www.autoscout24.be/nl/aanbod/' + graph_data.iloc[detail_index].at['guid'])
        
fig.canvas.mpl_connect('button_press_event', handle_focus)
# endregion


plot_graph(True)
plt.show()