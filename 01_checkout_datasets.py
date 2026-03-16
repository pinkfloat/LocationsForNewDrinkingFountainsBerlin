import pandas as pd
import geopandas as gpd

# Set display option to show all columns
pd.set_option('display.max_columns', None)

print("Drinking fountains (Berlin Open Data / BWB):")
fountains = gpd.read_file("Data/Drinking_Fountains/trinkwasserbrunnen_WGS84.geojson")
print(f"Number of drinking fountains: {len(fountains)}")
print(fountains.head())


print("\n\nLand use areas:")
print("Merged dataset from Berlin Open Data:")
berlin_area_df = gpd.read_file("Data/Land_Use/berlin_area_merged.geojson")
print(f"Number of areas in the dataset: {len(berlin_area_df)}")
print(berlin_area_df.head())


print("\n\nPublic transport stops:")
stops = pd.read_csv("Data/Stops/oepnv_02_osmnx_result.csv")
print(f"Number of stops in the OSM dataset (osmnx): {len(stops)}")
print(f"Number of entries with names: {stops['name'].notna().sum()}")
print(stops.head())


print("\n\nBeverage shops:")
stores = pd.read_csv("Data/Beverage_Stores/stores_02_osmnx_result.csv")
print(f"Number of stores in the OSM dataset (osmnx): {len(stores)}")
print(f"Number of entries with names: {stores['name'].notna().sum()}")
print(stores.head())
