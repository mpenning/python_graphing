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

def custom_ylim_range(df):
    """Return values to add 15% padding at the top and bottom of the y axis
    """
    diff = max(df) - min(df)
    minimum = min(df) - 0.15*diff
    maximum = max(df) + 0.15*diff
    return {'bottom': minimum, 'top': maximum}

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
df.index = pd.to_datetime(df.index)   # Cast index as datetime objects


## Get the figure and axes objects from matplotlib.pyplot (plt)
##
## 2 subplots, with the same X axis...
NUMBER_SUBPLOTS = 2
fig, ax = plt.subplots(nrows=NUMBER_SUBPLOTS, sharex=True)

## You can add more whitespace for the title, if you call this with  y=1.03
fig.suptitle('Time Series on 2018-07-25', fontsize=12)

## Plot the EWMA of the data, and manually override line names...
AXIS_PAD = 1.3
ax[0].plot(df.index, df['data01_ewma'], color='blue', label='this')
ax[0].legend(loc='lower left')
ax[0].set_title('Subplot stored in ax[0]', color='blue')   # AxesSubplot title
ax[0].set_ylim(**custom_ylim_range(df['data01_ewma']))     # Y-axis top/bottom
ax[0].grid(b=True)

ax[1].plot(df.index, df['data02_ewma'], color='red', label='that')
ax[1].legend(loc='lower left')
ax[1].set_title('Subplot stored in ax[1]', color='red')    # AxesSubplot title
ax[1].set_ylim(**custom_ylim_range(df['data02_ewma']))     # Y-axis top/bottom
ax[1].grid(b=False)

############################################################
###  Add vertical *shading* to the plot
############################################################

## pyplot requires the pandas index start and stop the shading
BEGIN_SHADE = '2018-07-25 14:45:00'
END_SHADE   = '2018-07-25 15:06:00'
begin_idx = df.index[
    df.index.get_loc(pd.to_datetime(BEGIN_SHADE), method='nearest')
    ]
end_idx   = df.index[
    df.index.get_loc(pd.to_datetime(END_SHADE), method='nearest')
    ]

# Add Vertical shading
ax[0].axvspan(begin_idx, end_idx, alpha=0.5, color='grey')
ax[1].axvspan(begin_idx, end_idx, alpha=0.5, color='grey')

############################################################
###  Annotate the beginning of the shaded area with an arrow
############################################################

## Generate coordinates of the arrow head at the beginning of the shaded area...
arrow_xcoord = mpdates.date2num(begin_idx) # This is a pyplot coordinate system
arrow_ycoord = df['data01_ewma'][begin_idx]

## Put annotation on the plot...
ax[0].annotate(
    s='Problem started here',            # Annotation string

    ## Coordinates of the arrow head...
    xy=(arrow_xcoord, arrow_ycoord), 

    # Coordinates of the left edge of the **arrow's text**... 
    #   textcoords indicates how the text placement is specified.  There are
    #   a lot of possibilities.  See the annotate() documentation for details
    textcoords='offset pixels',
    xytext=(-100, 175),

    va="center",
    ha="right",

    fontsize=8,   # Controls annotation text size

    clip_on=True,

    # connectionstyle parameters -
    #     angleA : starting angle of the path
    #     angleB : ending angle of the path
    #     armA : length of the starting arm
    #     armB : length of the ending arm
    #     rad : rounding radius of the edges
    #     connect(posA, posB)
    #
    #  Note: angle 0 is pointing right, and rotates clockwise.
    arrowprops=dict(
        arrowstyle="->",
        # Notes on relpos: https://stackoverflow.com/a/48216502/667301
        relpos=(0, 0.5),
        connectionstyle="angle,angleA=0,angleB=60",
        #connectionstyle="arc,armA=0,armB=0",
        )
    )


############################################################
###  Add the X-Axis labels on the lower graph
############################################################

# Format the x-axis ticks...
date_locator = mpdates.AutoDateLocator()
#timefmt = mpdates.DateFormatter('%Y-%m-%d %H:%M:%S')
timefmt = mpdates.DateFormatter('%H:%M:%S')  # Only show H:M:S on the graph...
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

fig.savefig('graph.png', bbox_inches='tight', dpi=300)
