import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import requests
from io import BytesIO
import webbrowser

# get data
filenames = [
    "lstmazdasort=standard&desc=0&cy=B&atype=C&ustate=N%2CU&powertype=kw",
    "lstsubaruforesterft_benzinemmmv=67%7C2023%7C%7C%2C67%7C2025%7C%7C&sort=standard&desc=0&cy=B&atype=C&ustate=N%2CU&fuel=B&powertype=kw&search_id=85cjksrqqa",
    "lsthondasort=standard&desc=0&cy=B&atype=C&ustate=N%2CU&powertype=kw",
]

frames = []
for name in filenames:
    frame = pd.read_csv('queries/' + name + '.csv', sep=",")
    frames.append(frame)

data = pd.concat(frames, ignore_index=True, sort=False)

# create figure
fig, (menu, graph, details) = plt.subplots(1, 3)
fig.suptitle = ""

# graph axes
graph.set(xlabel='mileage', ylabel='price')
scatter = graph.scatter(
    x=data['mileage'],
    y=data['price'],
    s=data['distance'],
    c=data['age'],
    cmap='YlOrRd'
)

# menu axes


# details axes
details.axis('off')
focused_listing = 0

def onclick(event):
    # array of points that got clicked
    did_hit_point, hit_info = scatter.contains(event)
    if did_hit_point:
        global focused_listing
        focused_listing = hit_info['ind'][0]
        print(focused_listing)
        response = requests.get(data.at[focused_listing, 'img-url'])
        img = Image.open(BytesIO(response.content))

        details.imshow(img)
        plt.draw()

    did_hit_details,_ = details.contains(event)
    if focused_listing and did_hit_details:
        webbrowser.open('https://www.autoscout24.be/nl/aanbod/' + data.at[focused_listing, 'guid'])
        

fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()
plt.draw()