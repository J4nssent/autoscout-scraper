
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
make_labels = makes
make_ax = fig.add_axes((V_OFFSET, 1-H_OFFSET-MK_HEIGHT, WDG_WIDTH, MK_HEIGHT))
make_check = wdg.CheckButtons(make_ax, makes)

def handle_make(label):
    label_index = makes.index(label)
    was_checked = not make_check.get_status()[label_index]
    global focused_make
    if was_checked and label is not focused_make:   
        print("focus")
        make_check.eventson = False
        make_check.set_active(label_index)
        make_check.eventson = True
        focused_make = label
    else:
        if was_checked:
            focused_make = None
        else:
            focused_make = label

        # global make_msk
        # make_msk = [(not b if listings.at[i, 'make'] == label else b) for i, b in enumerate(make_msk)]

        global listings, model_msk
        model_msk = [False] * len(listings.index)
        if not listings.empty and label in listings.make.unique():
            print("drop")
            listings.drop(listings[listings.make == label].index)
        else:
            print("concat:", 'listings/' + label + '.csv')
            l = pd.read_csv('listings/' + label + '.csv')
            print(l)
            listings = pd.concat([listings, l], ignore_index=True)
            global age_msk, distance_msk
            age_msk = distance_msk = [True] * len(listings.index)
 
    plot_models(focused_make)
    plot_graph()
    
make_check.on_clicked(handle_make)
# endregion

# region model checkboxes
model_msk = [False] * len(listings.index)
model_ax = fig.add_axes((2*V_OFFSET+WDG_WIDTH, H_OFFSET, WDG_WIDTH, MD_HEIGHT))
model_check = None

def plot_models(make):
    model_ax.clear()
    print(listings)
    models = sorted(map(str, listings[listings.make == make].model.unique()))
    global model_check
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


# region price slider
price_msk = [True] * len(listings.index)
price_ax = fig.add_axes((V_OFFSET, H_OFFSET, WDG_WIDTH, SLDR_HEIGHT))
price_slide = wdg.Slider(
    ax=price_ax,
    label='price',
    valmin=0,
    valmax=20000,
    valinit=MAX_PRC
)

def handle_price(val):
    # global price_msk
    # price_msk = [p < val for p in listings.price]
    graph_ax.set_ylim(None, val)
    plot_graph()

price_slide.on_changed(handle_price)
# endregion

# region mileage slider
mileage_msk = [True] * len(listings.index)
mileage_ax = fig.add_axes((V_OFFSET, H_OFFSET + 2*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT))
mileage_slide = wdg.Slider(
    ax=mileage_ax,
    label='mileage',
    valmin=0,
    valmax=500000,
    valinit=MAX_MLG
)

def handle_mileage(val):
    # global mileage_msk
    # mileage_msk = [m < val for m in listings.mileage]
    graph_ax.set_xlim(None, val)
    plot_graph()

mileage_slide.on_changed(handle_mileage)
# endregion

# region age slider
age_msk = [True] * len(listings.index)
age_ax = fig.add_axes((V_OFFSET, H_OFFSET + 4*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT))
age_slide = wdg.Slider(
    ax=age_ax,
    label='age (yr)',
    valmin=0,
    valmax=25,
    valinit=25
)

def handle_age(val):
    global age_msk
    age_msk = [a < val * 365 for a in listings['reg-age']]
    plot_graph()

age_slide.on_changed(handle_age)
# endregion

# region distance slider
distance_msk = [True] * len(listings.index)
distance_ax = fig.add_axes((V_OFFSET, H_OFFSET + 6*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT))
distance_slide = wdg.Slider(
    ax=distance_ax,
    label='distance (km)',
    valmin=0,
    valmax=200,
    valinit=200
)

def handle_distance(val):
    global distance_msk
    distance_msk = [d < val for d in listings.distance]
    plot_graph()

distance_slide.on_changed(handle_distance)
# endregion


# scatter graph
lim_x, lim_y = MAX_MLG, MAX_MLG
scatter = None
graph_ax.set(
    xlabel='mileage',
    ylabel='price',
    frame_on=True,
)

def plot_graph(init=False):
    graph_ax.clear() # TODO: clear scatter instead of axes (scatter.remove)
    graph_ax.set_xlim(0, MAX_MLG)
    graph_ax.set_ylim(0, MAX_PRC)

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

    


# detail section
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
    if scatter is not None:
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