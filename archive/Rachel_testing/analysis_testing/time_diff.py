
import geopandas as gp, pandas as pd, numpy as np

# def read_huc8_shp(gdrive, folder):
#     natural = gp.read_file(gdrive+folder+"all_basins_no_dams/huc8_indices.shp")
#     b1920 = gp.read_file(gdrive+folder+"all_basins_before_1920/huc8_indices.shp")
#     b1950 = gp.read_file(gdrive+folder+"all_basins_before_1950/huc8_indices.shp")
#     b1980 = gp.read_file(gdrive+folder+"all_basins_before_1980/huc8_indices.shp")
#     unfil = gp.read_file(gdrive+folder+"all_basins_unfiltered/huc8_indices.shp")

    # return natural, b1920, b1950, b1980, unfil

def frag_diff(gdrive, folder):
    # read_results = read_huc8_shp(gdrive, folder)
    # natural bifurcation
    natural = gp.read_file(gdrive+folder+"all_basins_no_dams/huc8_indices.shp")

    #before 1920 bifurcation
    b1920 = gp.read_file(gdrive+folder+"all_basins_before_1920/huc8_indices.shp")
    b1920["frag_diff"] = b1920["LENGTHKM_l"] -  natural["LENGTHKM_l"]
    b1920.to_file(gdrive+folder+"huc8_b1920_frag_diff.shp")
    b1920_cum = b1920.copy()  #cumulative fragment difference
    b1920_cum["frag_cudiff"] = b1920["LENGTHKM_l"] -  natural["LENGTHKM_l"]
    b1920.to_file(gdrive+folder+"huc8_b1920_frag_cudiff.shp")
    print("1920 to shp complete")

    #before 1950 bifurcation
    b1950 = gp.read_file(gdrive+folder+"all_basins_before_1950/huc8_indices.shp")
    b1950["frag_diff"] = b1950["LENGTHKM_l"] -  b1920["LENGTHKM_l"]
    b1950.to_file(gdrive+folder+"huc8_b1950_frag_diff.shp")
    b1950_cum = b1950.copy()   #cumulative fragment difference
    b1950_cum["frag_cudiff"] = (b1950["LENGTHKM_l"] -  b1920["LENGTHKM_l"])+b1920["frag_diff"]
    b1950.to_file(gdrive+folder+"huc8_b1980_frag_cudiff.shp")
    print("1950 to shp complete")

    #before 1980 bifurcation
    b1980 = gp.read_file(gdrive+folder+"all_basins_before_1980/huc8_indices.shp")
    b1980["frag_diff"] = b1980["LENGTHKM_l"] -  b1950["LENGTHKM_l"]
    b1980.to_file(gdrive+folder+"huc8_b1950_frag_diff.shp")
    b1980_cum = b1980.copy()   #cumulative fragment difference
    b1980_cum["frag_cudiff"] = (b1980["LENGTHKM_l"] -  b1950["LENGTHKM_l"])+b1920["frag_diff"]+b1950["frag_diff"]
    b1980.to_file(gdrive+folde+"huc8_b1980_frag_cudiff.shp")
    print("1980 to shp complete")

    #2010 bifurcation
    unfil = gp.read_file(gdrive+folder+"all_basins_unfiltered/huc8_indices.shp")
    unfil["frag_diff"] = unfil["LENGTHKM_l"] -  b1980["LENGTHKM_l"]
    unfil.to_file(gdrive+folder+"huc8_unfil_frag_diff.shp")
    unfil_cum = unfil.copy()   #cumulative fragment difference
    unfil_cum["frag_cudiff"] = (unfil["LENGTHKM_l"] -  b1980["LENGTHKM_l"])+b1920["frag_diff"]+b1950["frag_diff"]+b1980["frag_diff"]
    unfil.to_file(gdrive+folder+"huc8_unfil_frag_cudiff.shp")
    print("2010 to shp complete")

def stor_diff(gdrive, folder):
    # natural bifurcation
    natural = gp.read_file(gdrive+folder+"no_dams/huc8_indices_no_dams.shp")
    natural = natural[["States", "HUC8_no", "Norm_stor_", "Norm_sto_1", "Norm_sto_2"]]

    #before 1920 bifurcation
    bf1920 = gp.read_file(gdrive+folder+"1920/huc8_indices_1920.shp")
    bf1920 = bf1920[["States", "HUC8_no", "Norm_stor_", "Norm_sto_1", "Norm_sto_2", "geometry"]]
    b1920 = gp.GeoDataFrame(bf1920, geometry='geometry')
    b1920["stor_diff"] = b1920["Norm_sto_1"] -  natural["Norm_sto_1"]
    b1920.to_file(gdrive+folder+"1920/huc8_b1920_stor_diff.shp")
    b1920_cum = b1920.copy()  #cumulative fragment difference
    b1920_cum["stor_cudiff"] = b1920["stor_diff"] -  natural["stor_diff"]
    b1920.to_file(gdrive+folder+"1920/huc8_b1920_stor_cudiff.shp")
    print("1920 to shp complete")

    #before 1950 bifurcation
    b1950 = gp.read_file(gdrive+folder+"1950/huc8_indices_1950.shp")
    b1950 = b1950[["States", "HUC8_no", "Norm_stor_", "Norm_sto_1", "Norm_sto_2", "geometry"]]
    b1950 = gp.GeoDataFrame(b1950, geometry='geometry')
    b1950["stor_diff"] = b1950["stor_diff"] -  b1920["stor_diff"]
    b1950.to_file(gdrive+folder+"1950/huc8_b1950_stor_diff.shp")
    b1950_cum = b1950.copy()   #cumulative fragment difference
    b1950_cum["stor_cudiff"] = (b1950["stor_diff"] -  b1920["stor_diff"])+b1920["stor_diff"]
    b1950.to_file(gdrive+folder+"1950/huc8_b1980_stor_cudiff.shp")
    print("1950 to shp complete")

    #before 1980 bifurcation
    b1980 = gp.read_file(gdrive+folder+"1980/huc8_indices_1980.shp")
    b1980 = b1980[["States", "HUC8_no", "Norm_stor_", "Norm_sto_1", "Norm_sto_2", "geometry"]]
    b1980 = gp.GeoDataFrame(b1980, geometry='geometry')
    b1980["stor_diff"] = b1980["stor_diff"] -  b1950["stor_diff"]
    b1980.to_file(gdrive+folder+"1980/huc8_b1950_stor_diff.shp")
    b1980_cum = b1980.copy()   #cumulative fragment difference
    b1980_cum["stor_cudiff"] = (b1980["stor_diff"] -  b1950["stor_diff"])+b1920["stor_diff"]+b1950["stor_diff"]
    b1980.to_file(gdrive+folde+"1980/huc8_b1980_stor_cudiff.shp")
    print("1980 to shp complete")

    #2010 bifurcation
    unfil = gp.read_file(gdrive+folder+"2010/huc8_indices_2010.shp")
    unfil = unfil[["States", "HUC8_no", "Norm_stor_", "Norm_sto_1", "Norm_sto_2", "geometry"]]
    unfil = gp.GeoDataFrame(unfil, geometry='geometry')
    unfil["stor_diff"] = unfil["stor_diff"] -  b1980["stor_diff"]
    unfil.to_file(gdrive+folder+"2010/huc8_unfil_stor_diff.shp")
    unfil_cum = unfil.copy()   #cumulative fragment difference
    unfil_cum["stor_cudiff"] = (unfil["stor_diff"] -  b1980["stor_diff"])+b1920["stor_diff"]+b1950["stor_diff"]+b1980["stor_diff"]
    unfil.to_file(gdrive+folder+"2010/huc8_unfil_stor_cudiff.shp")
    print("2010 to shp complete")