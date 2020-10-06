# Things to add to segGeo
- Reachcode
- HUC 2
- HUC 4
- HUC 8

# About the dissolve feature
I do not think we want to use dissolve because we would need the flowlines as a polygon. The polygon for each HUC has only one entry in the attribute table. We could average indices by HUC using the REACHCODE and then add that value to the correct HUC to get the desired result. 

Pseudo code
    - Add x number of columns with the corresponding HUC for that flowline in segGeo
    - Aggregate by desired HUC (2,4,8)
        - groupby or pivot table
        - Append that value to the HUC shapefile or a HUC csv
    - Append all the desired indices to the HUC
    - Read HUC into QGIS and plot!