import pandas as pd

# Set display option to show all columns
pd.set_option('display.max_columns', None)

print("Trinkbrunnen (von Geoportal Berlin):")
trinkbrunnen_df = pd.read_csv("Trinkbrunnen/trinkbrunnen_berlin.csv")
print(f"Num Trinkbrunnen: {len(trinkbrunnen_df)}")
print(trinkbrunnen_df.head())


print("\n\nGrünanlagen:")
print("\n\nQuelle Geo Portal Berlin:")
gruenanlagen_geo_portal_df = pd.read_csv("Gruenanlagen/Quelle_Geoportal_Berlin/gruenanlagen_berlin.csv")
print(f"Num Grünanlagen in Geo Portal Berlin: {len(gruenanlagen_geo_portal_df)}")
print(f"Num von Eintraegen mit Namen: {gruenanlagen_geo_portal_df["namenr"].notna().sum()}")
print(gruenanlagen_geo_portal_df.head())

print("\n\nQuelle OSM x Overpass API:")
gruenanlagen_osm_overpass_df = pd.read_csv("Gruenanlagen/Quelle_Openstreetmap/gruenanlagen_01_overpass_result.csv")
print(f"Num Grünanlagen in OSM Dataset (overpass): {len(gruenanlagen_osm_overpass_df)}")
print(f"Num von Eintraegen mit Namen: {gruenanlagen_osm_overpass_df["name"].notna().sum()}")
print(gruenanlagen_osm_overpass_df.head())

print("\n\nQuelle OSMNX:")
gruenanlagen_osmnx_df = pd.read_csv("Gruenanlagen/Quelle_Openstreetmap/gruenanlagen_02_osmnx_result.csv")
print(f"Num Grünanlagen in OSM Dataset (osmnx): {len(gruenanlagen_osmnx_df)}")
print(f"Num von Eintraegen mit Namen: {gruenanlagen_osmnx_df["name"].notna().sum()}")
print(gruenanlagen_osmnx_df.head())


print("\n\nHaltestellen:")
print("\n\nQuelle OSM x Overpass API:")
haltestellen_osm_overpass_df = pd.read_csv("Haltestellen/Quelle_Openstreetmap/oepnv_01_overpass_result.csv")
print(f"Num Haltestellen in OSM Dataset (overpass): {len(haltestellen_osm_overpass_df)}")
print(f"Num von Eintraegen mit Namen: {haltestellen_osm_overpass_df["name"].notna().sum()}")
print(haltestellen_osm_overpass_df.head())

print("\n\nQuelle OSMNX:")
haltestellen_osmnx_df = pd.read_csv("Haltestellen/Quelle_Openstreetmap/oepnv_02_osmnx_result.csv")
print(f"Num Haltestellen in OSM Dataset (osmnx): {len(haltestellen_osmnx_df)}")
print(f"Num von Eintraegen mit Namen: {haltestellen_osmnx_df["name"].notna().sum()}")
print(haltestellen_osmnx_df.head())