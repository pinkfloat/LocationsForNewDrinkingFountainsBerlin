import pandas as pd
import geopandas as gpd

# Set display option to show all columns
pd.set_option('display.max_columns', None)

usage_df = gpd.read_file("flaechennutzung2022_WGS84.geojson")
population_df = gpd.read_file("einwohnerdichte2023_WGS84.geojson")

# print("\n\nFlächennutzung:")
# print(usage_df.head())

# print("\n\nEinwohnerdichte:")
# print(population_df.head())

print("\n\nCheck if all keys match between datasets:")
print(
    usage_df["schluessel"].isin(population_df["schluessel"]).all()
)

##### MERGE #####
population_subset = population_df[[
    "schluessel",
    "ew2023",
    "ew_ha_2023"
]]

# keep all columns of usage_df in here
merged_gdf = usage_df.merge(
    population_subset,
    on="schluessel",
    how="left"
)

# only keep these columns of merged_df
final_gdf = merged_gdf[[
    "schluessel",
    "bezirk",
    "nutz",
    "enutzung",
    "typ",
    "etypklar",
    "ew2023",
    "ew_ha_2023",
    "geometry"
]]

print("\n\nResult:")
print(final_gdf.head())

final_gdf.to_file("berlin_area_merged.geojson", driver="GeoJSON")
