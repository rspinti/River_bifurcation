# Workflow Outline

- Open run_workflow.py
    - Specify the folder and path for the output
    - Specify the basins to run 
- Run run_workflow.py in terminal or IDE
    - Packages and modules are loaded
    - The folder and location of the output are specified
    - The basin list is created with basin names to be run
    - The basin list is read into the create_basin_csvs to check if the each basin has a csv in the output folder
        - If there is no csv for the specified basin, a csv is created from NHD and NABD from the basin name
    - For each basin in the list:
        - The basin csv is read in as a segments dataframe
        - The units of QC_MA and Normal Storage are converted from cfs/ac-feet to cubic meters
        - Specified columns are aggregated by upstream components
        - Create a list for each
        - Calculate DOR (storage/QC_MA)
            - Give a value of -1 to locations where QC_MA is 0 and storage is positive
            - Give a value of 0 to anywhere that Norm_stor_up is 0 (results in NAs when norm stor up is 0 and q is 0)
        - Make fragments by walking downstream until a dam is hit
        - Aggregate by fragment
        - Calculate DCI (length upstream squared/ total length of network squared)
            - use fragments to find length^2
        - Add DCI to segments by merging on Frag
        - Aggregate variables by HUC 2, 4, or 8
            - Sum Norm_stor, Dam count, and length by specified HUC
            - Find mean of fragment length
            - What is this? HUC_summary["Frag_Count"] = HUC_summaryf['LENGTHKM']['len']
            - Find the outlet of each HUC by taking the segment with the largest upstream Length
                - Use the outlet segment ID to find the Frag, Length upstream, and DOR at the HUC outlet
        - Create the SegGeo dataframe, which has variables of interest and their location by segment


