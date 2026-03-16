import pandas as pd
import geopandas as gpd

# Set display option to show all columns
pd.set_option('display.max_columns', None)

print("Drinking fountains (Berlin Open Data / BWB):")
trinkbrunnen_gdf = gpd.read_file("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
print(f"Number of drinking fountains: {len(trinkbrunnen_gdf)}")
print(trinkbrunnen_gdf.head())


print("\n\nLand use areas:")
print("Merged dataset from Berlin Open Data:")
berlin_area_df = gpd.read_file("Flaechennutzung/berlin_area_merged.geojson")
print(f"Number of areas in the dataset: {len(berlin_area_df)}")
print(berlin_area_df.head())


print("\n\nPublic transport stops:")
haltestellen_osmnx_df = pd.read_csv("Haltestellen/oepnv_02_osmnx_result.csv")
print(f"Number of stops in the OSM dataset (osmnx): {len(haltestellen_osmnx_df)}")
print(f"Number of entries with names: {haltestellen_osmnx_df['name'].notna().sum()}")
print(haltestellen_osmnx_df.head())


print("\n\nBeverage shops:")
stores_osmnx_df = pd.read_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")
print(f"Number of stores in the OSM dataset (osmnx): {len(stores_osmnx_df)}")
print(f"Number of entries with names: {stores_osmnx_df['name'].notna().sum()}")
print(stores_osmnx_df.head())
