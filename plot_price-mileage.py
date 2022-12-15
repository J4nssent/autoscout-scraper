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
    global focused_make, listings, model_msk
    if was_checked:
        if label is not focused_make:   
            make_check.eventson = False
            make_check.set_active(label_index)
            make_check.eventson = True
        else:
            if not listings.empty and label in listings.make.unique():
                indices = listings[listings.make == label].index
                listings.drop(indices, inplace=True)
                for i in reversed(indices):
                    del model_msk[i]
            focused_make = None
    else:
        data = pd.read_csv('listings/' + label + '.csv')
        listings = pd.concat([listings, data], ignore_index=True)
        model_msk.extend([False] * len(data.index))
        
    focused_make = label
    plot_models()
    
make_check.on_clicked(handle_make)
# endregion

# region model checkboxes
model_msk = []
model_ax = fig.add_axes((2*V_OFFSET+WDG_WIDTH, H_OFFSET, WDG_WIDTH, MD_HEIGHT))
model_check = None

def handle_model(label):
    global model_msk
    model_msk = [(not b if listings.at[i, 'model'] == label else b) for i, b in enumerate(model_msk)]
    plot_graph()

def plot_models():
    model_ax.clear()
    models = sorted(map(str, listings[listings.make == focused_make].model.unique()))
    global model_check
    model_check = wdg.CheckButtons(model_ax, models)
    model_check.on_clicked(handle_model)
    plt.draw()

# endregion

# region sliders
sliders = [
    {
        'label': 'price',
        'min': 0, 'max': 20000, 'init': MAX_PRC,
        'var': 'lim_y'
    },{
        'label': 'mileage',
        'min': 0, 'max': 500000, 'init': MAX_MLG,
        'var': 'lim_x'
    },{
        'label': 'age (yr)',
        'min': 0, 'max': 25, 'init': 25,
        'var': 'max_age'
    },{
        'label': 'distance (km)',
        'min': 0, 'max': 200, 'init': 200,
        'var': 'max_distance'
    },
]

def update(name):
    def callback(val):
        globals()[name] = val
        globals()['plot_graph']()
    return callback

for i, s in enumerate(sliders):
    ax = fig.add_axes((V_OFFSET, H_OFFSET + i*SLDR_HEIGHT, WDG_WIDTH, SLDR_HEIGHT))
    s['slider'] = wdg.Slider(
        ax=ax,
        label=s['label'],
        valmin=s['min'],
        valmax=s['max'],
        valinit=s['init']
    )
    s['slider'].on_changed(update(s['var']))
    s['slider'].set_val(s['init'])
# endregion

# scatter graph
scatter = None

def reset_graph_ax():
    print('reset_graph_ax')
    graph_ax.clear()
    graph_ax.set_xlim(0, lim_x)
    graph_ax.set_ylim(0, lim_y)
    graph_ax.grid(
        visible=True, 
        which='both'
    )
    graph_ax.set(
        xlabel='mileage',
        ylabel='price',
        frame_on=True,
    )

def plot_graph():
    reset_graph_ax()

    if not listings.empty:
        age_msk = [a < max_age * 365 for a in listings.get('reg-age')]
        distance_msk = [d < max_distance for d in listings.get('distance')]

        mask = reduce(np.logical_and, (age_msk, distance_msk, model_msk))

        global graph_data
        graph_data = listings[mask]

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

        graph_ax.set_xlim(0, lim_x)
        graph_ax.set_ylim(0, lim_y)

    plt.draw()


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

plt.show()