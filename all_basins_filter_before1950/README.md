# River bifurcation - All basins filtering dams constructed prior to 1950
### Created November 12, 2020

This folder contains the scripts needed to run the extract and bifurcate scripts.
The extract script creates csvs for each river basin to be run in Network
Metrics. Then, the bifurcate functions are used to aggregate by upstream 
attributes and to add these to a csv for plotting in QGIS.

Contained in this folder:
    *average_by_HUC.py*
    *bifurcate.py*
    *create_csvs.py*
    *extract.py*
    *read_csvs.py*
    *run_workflow.py*
