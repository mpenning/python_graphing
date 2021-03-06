# Overview

The script named `build_graph.py` in this directory is an example of graping
two time-series with the same x-axis (i.e. the same timeframes).

This is what the output of the graph looks like.  The lines are randomly
generated; the image below is typical of what the graph will look like.

![output graph](https://raw.githubusercontent.com/mpenning/python_graphing/master/subplots_labels_shading/graph.png)

The input time-series data comes from a list of dictionaries.  The data is not
very smooth, so I build an ewma with pandas, and the graphs you see are the 
ewma lines.

The following modules are required to run this script:

- matplotlib  (Using version 2.2.2 when I wrote this)
- pandas  (Using version 0.23.3 when I wrote this)

The script should be documented well enough.  Nothing in this script is 
particularly innovative; I'm just keeping it here because there are so many
details involved in building one of these graphs.
