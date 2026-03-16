import pandas as pd
import geopandas as gpd

# Set display option to show all columns
pd.set_option('display.max_columns', None)

print("Trinkbrunnen (Berlin Open Data / BWB):")
trinkbrunnen_gdf = gpd.read_file("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
print(f"Num Trinkbrunnen: {len(trinkbrunnen_gdf)}")
print(trinkbrunnen_gdf.head())


print("\n\nFlächen insgesamt:")
print("\n\nMerged Data Set von Berlin Open Data:")
berlin_area_df = gpd.read_file("Flaechennutzung/berlin_area_merged.geojson")
print(f"Num Flächen im Dataset: {len(berlin_area_df)}")
print(berlin_area_df.head())


print("\n\nHaltestellen:")
haltestellen_osmnx_df = pd.read_csv("Haltestellen/oepnv_02_osmnx_result.csv")
print(f"Num Haltestellen in OSM Dataset (osmnx): {len(haltestellen_osmnx_df)}")
print(f"Num von Eintraegen mit Namen: {haltestellen_osmnx_df["name"].notna().sum()}")
print(haltestellen_osmnx_df.head())


print("\n\nGetränkeläden:")
stores_osmnx_df = pd.read_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")
print(f"Num Stores in OSM Dataset (osmnx): {len(stores_osmnx_df)}")
print(f"Num von Eintraegen mit Namen: {stores_osmnx_df["name"].notna().sum()}")
print(stores_osmnx_df.head())
