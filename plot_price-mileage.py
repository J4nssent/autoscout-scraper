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
MIN_PRC = 10000
MAX_PRC = 30000
INIT_PRC = 30000
MAX_MLG = 200000
INIT_MLG = 100000
MAX_AGE = 15
INIT_AGE = 12
MAX_DIST = 400
INIT_DIST = 150
DEFAULT_CHECKED = True

# constants
WIN_WIDTH, WIN_HEIGHT = 23, 9

V_OFFSET = 0.05
H_OFFSET = 0.1
WDG_WIDTH = 0.1
SLDR_HEIGHT = 0.03
MK_HEIGHT = 0.5
MD_HEIGHT = 0.8
FL_HEIGHT = 0.06

# data
makes = [s.replace('.csv','') for s in listdir('listings')]
listings = pd.DataFrame()

# axes
fig, (menu_ax, graph_ax, detail_ax) = plt.subplots(1, 3, figsize=[WIN_WIDTH, WIN_HEIGHT])
menu_ax.axis('off')
detail_ax.axis('off')

# scatter graph
scatter = None
lim_x, lim_y = INIT_MLG, INIT_PRC
max_vehicle_age, max_distance = INIT_AGE, INIT_DIST

def reset_graph_ax():
    graph_ax.clear()
    graph_ax.set_xlim(0, lim_x)
    graph_ax.set_ylim(MIN_PRC, lim_y)
    graph_ax.grid(
        visible=True, 
        which='both'
    )
    graph_ax.set(
        xlabel='mileage',
        ylabel='price',
        frame_on=True,
    )

def plot_graph(_=None):
    global graph_data, scatter

    if listings.empty:
        # clear scatter (keep artist)
        scatter.set_offsets(np.empty((0, 2)))
        scatter.set_sizes(np.array([]))
        scatter.set_array(np.array([]))
        graph_ax.set_xlim(0, lim_x)
        graph_ax.set_ylim(MIN_PRC, lim_y)
        fig.canvas.draw_idle()
        return

    # --- vectorized masks ---
    age_msk = (listings['reg-age'].to_numpy() < (max_vehicle_age * 365))
    distance_msk = (listings['distance'].to_numpy() < max_distance)

    # map fuel types using current checkbox dict
    # fuel_msk = listings['fuel-type'].map(lambda t: fuel_types.get(t, False)).to_numpy(dtype=bool)

    model_msk_np = np.asarray(model_msk, dtype=bool)

    mask = age_msk & distance_msk & model_msk_np # & fuel_msk

    graph_data = listings.loc[mask]

    # --- update scatter in place ---
    x = graph_data['mileage'].to_numpy()
    y = graph_data['price'].to_numpy()
    offsets = np.column_stack((x, y))
    scatter.set_offsets(offsets)

    # sizes and colors
    scatter.set_sizes(graph_data['distance'].to_numpy())     # s expects points^2; scale if needed
    scatter.set_array(graph_data['reg-age'].to_numpy())      # drives colormap

    # axes limits (no clear)
    graph_ax.set_xlim(0, lim_x)
    graph_ax.set_ylim(MIN_PRC, lim_y)

    fig.canvas.draw_idle()

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
            plot_graph()
    else:
        data = pd.read_csv('listings/' + label + '.csv')
        listings = pd.concat([listings, data], ignore_index=True)
        model_msk.extend([DEFAULT_CHECKED] * len(data.index))
        
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
    model_msk = [(not b if listings['model'].iat[i] == label else b) for i, b in enumerate(model_msk)]
    plot_graph()

def plot_models():
    model_ax.clear()
    models = sorted(map(str, listings[listings.make == focused_make].model.unique()))
    global model_check
    model_check = wdg.CheckButtons(model_ax, models, [DEFAULT_CHECKED] * len(models))
    if DEFAULT_CHECKED:
        plot_graph()
    model_check.on_clicked(handle_model)
    plt.draw()
# endregion

# fuel type checkbox
# fuel_types = {'b': True, 'd': True}
# fuel_ax = fig.add_axes((V_OFFSET, 1-MK_HEIGHT-2*H_OFFSET, WDG_WIDTH, FL_HEIGHT))
# fuel_check = wdg.CheckButtons(fuel_ax, ['benzine', 'diesel'], fuel_types.values())

# def handle_fuel(label):
#     fuel_types[label[0]] = not fuel_types[label[0]]

# fuel_check.on_clicked(handle_fuel)
# fuel_check.on_clicked(plot_graph)

# region sliders
sliders = [
    {
        'label': 'price',
        'min': 0, 'max': MAX_PRC, 'init': INIT_PRC,
        'var': 'lim_y'
    },{
        'label': 'mileage',
        'min': 0, 'max': MAX_MLG, 'init': INIT_MLG,
        'var': 'lim_x'
    },{
        'label': 'age (yr)',
        'min': 0, 'max': MAX_AGE, 'init': INIT_AGE,
        'var': 'max_vehicle_age'
    },{
        'label': 'distance (km)',
        'min': 0, 'max': MAX_DIST, 'init': INIT_DIST,
        'var': 'max_distance'
    # },{
    #     'label': 'listing age (days)',
    #     'min': 0, 'max': 2000, 'init': 2000,
    #     'var': 'max_listing_age'
    },
]

def update(name):
    def callback(val):
        globals()[name] = val
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
    s['slider'].on_changed(plot_graph)
# endregion

# region detail section
detail_index = None
detail_img_ax = fig.add_axes((0.67, 0.45, 0.28, 0.45))
detail_img_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ax = fig.add_axes((0.67, H_OFFSET, 0.28, 0.3))
detail_text_ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
detail_text_ar = None

detail_tmpl = '''
    make:       {make}              price:          {price}

    model:      {model}             fuel type:      {fuel-type}

    year:       {first-reg-date}    mileage:        {mileage} km


    seller:             {seller-type}                  

    listing age:        #listing-age# days

    distance:           {distance:.0f}
'''


img_ar = None
def draw_image(index=None):
    images = detail_listing.at['images']

    global img_index
    if index is None:
        img_index = (img_index + 1) % len(images)
    else:
        img_index = index

    img_url = images.split(' ')[img_index][:-13]
    res = requests.get(img_url)
    img_data = Image.open(BytesIO(res.content))

    global img_ar
    img_ar = detail_img_ax.imshow(img_data)

def draw_details():
    global detail_listing
    detail_listing = graph_data.iloc[detail_index]

    # image
    draw_image(0)

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
    
    if detail_index is not None and detail_text_ar.contains(e)[0]:
        webbrowser.open('https://www.autoscout24.be/nl/aanbod/' + graph_data.iloc[detail_index].at['guid'])
    
    if img_ar is not None and img_ar.contains(e)[0]:
        draw_image()
        plt.draw()
        
fig.canvas.mpl_connect('button_press_event', handle_focus)
# endregion

reset_graph_ax()
graph_ax.grid(True, which='both')
graph_ax.set_xlabel('mileage')
graph_ax.set_ylabel('price')

scatter = graph_ax.scatter(
    [], [],                 # empty data
    s=[],                   # sizes
    c=[],                   # colors
    cmap='YlOrRd',
    norm=Normalize(0, MAX_AGE * 365)
)

plt.show()