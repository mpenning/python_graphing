from datetime import datetime, timedelta
from random import random, seed
from pprint import pprint

import matplotlib.dates as mpdates
import matplotlib
matplotlib.use('Agg')  # This is required before importing pyplot (run headless)

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_random_data(length, start_value):
    """Generate some random data.
        length (int): Number of data points
        start_value (float): Starting value
    """
    prob = [0.90, 0.10]  # [Probability_up, probability_down]
    retval = [float(start_value)]
    rr = np.random.random(int(length) - 1)
    upp = rr > prob[0]
    downp = rr < prob[1]
    for idownp, iupp in zip(downp, upp):
        down = idownp and retval[-1] > 1
        up = iupp and retval[-1] < 4
        if random()>0.5:
            val = (retval[-1] - down + up) + random()
        else:
            val = (retval[-1] - down + up) - random()
        retval.append(val)
    return retval

############################################################
###  Generate random data
############################################################
START = datetime(2018, 7, 25, 14, 0, 0)

## Generate y-axis data...
yaxis_random01 = generate_random_data(7200, 2.2)
yaxis_random02 = generate_random_data(7200, 2.8)

## Generate some time stamps (x axis)...
xaxis_time = list()
for offset_sec in range(0, 7200):
    ts = START + timedelta(seconds=offset_sec)
    xaxis_time.append(ts)

############################################################
###  Plot data below
############################################################

# Add the first series...
data = [{'time': x, 'data01': y} for x, y in zip(xaxis_time, yaxis_random01)]
df = pd.DataFrame.from_dict(data)

# Add the second series
df['data02'] = yaxis_random02

# Moving Average for the data...
df['data01_ewma'] = df['data01'].ewm(com=60).mean()
df['data02_ewma'] = df['data02'].ewm(com=100).mean()

## Force the df index to be the time column
df.set_index('time', inplace=True)


## Get the figure and axes objects from matplotlib.pyplot (plt)
##
## 2 subplots, with the same X axis...
NUMBER_SUBPLOTS = 2
fig, ax = plt.subplots(nrows=NUMBER_SUBPLOTS, sharex=True)

## Add a graph title and ensure it's not overlapping graph (i.e. y=1.06)
fig.suptitle('Time Series on 2018-07-25', fontsize=12, y=1.06)

## Plot the EWMA of the data, and manually override line names...
ax[0].plot(df.index, df['data01_ewma'], color='blue', label='this')
ax[0].legend(loc='lower left')
ax[0].set_title('Subplot stored in ax[0]')   ### <--- This does nothing
ax[0].grid(b=True)

ax[1].plot(df.index, df['data02_ewma'], color='red', label='that')
ax[1].legend(loc='lower left')
ax[1].set_title('Subplot stored in ax[1]')   ### <--- This does nothing
ax[1].grid(b=False)

############################################################
###  Add vertical *shading* to the plot
############################################################

## Shade an area to highlight something...
BEGIN_SHADE = '2018-07-25 14:45:00'
END_SHADE   = '2018-07-25 15:06:00'
begin_idx = df.index[
    df.index.get_loc(pd.to_datetime(BEGIN_SHADE), method='nearest')
    ]
end_idx   = df.index[
    df.index.get_loc(pd.to_datetime(END_SHADE), method='nearest')
    ]

ax[0].axvspan(begin_idx, end_idx, alpha=0.5, color='grey')
ax[1].axvspan(begin_idx, end_idx, alpha=0.5, color='grey')

############################################################
###  Annotate the beginning of the shaded area with an arrow
############################################################

## Generate coordinates of the arrow head at the beginning of the shaded area...
xcoord = mpdates.date2num(begin_idx)
ycoord = df['data01_ewma'][begin_idx]

## Generate coordinates of the annotation text...
X_OFFSET_MINUTES = 45
Y_OFFSET_MULTIPLE = 2.0
text_xcoord = mpdates.date2num(begin_idx-timedelta(minutes=X_OFFSET_MINUTES))
text_ycoord = ycoord*Y_OFFSET_MULTIPLE

## Put annotation on the plot...
ax[0].annotate('Problem started here',

    ## Coordinates of the arrow head...
    xy=(xcoord, ycoord), 

    # Coordinates of the arrow text...
    textcoords='data',
    xytext=(text_xcoord, text_ycoord),

    clip_on=True,
    arrowprops=dict(arrowstyle='->',
        connectionstyle='arc,angleA=0,armA=50,rad=10')
    )


############################################################
###  Add the X-Axis labels on the lower graph
############################################################

# Format the x-axis ticks...
date_locator = mpdates.AutoDateLocator()
#timefmt = mpdates.DateFormatter('%Y-%m-%d %H:%M:%S')
timefmt = mpdates.DateFormatter('%H:%M:%S')
ax[1].xaxis.set_major_formatter(timefmt)
for tick in ax[1].get_xticklabels():
    tick.set_rotation(90)

############################################################
###  Plot the graph...
############################################################

## Specify font info
font = {'family': 'DejaVu Sans',
    'weight': 'bold',
    'size': 10}
matplotlib.rc('font', **font)

fig.tight_layout(pad=2)       # labels don't run off the plot w/ 0.75" margins
fig.subplots_adjust(top=0.88) # https://stackoverflow.com/a/35676071/667301
fig.savefig('graph.png', bbox_inches='tight')
