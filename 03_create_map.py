import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# -------------------------------------------------
# Copied from clean_data script to transform csv
# data into geo dataframes
# -------------------------------------------------
pd.set_option('display.max_columns', None)
green_spaces_df = pd.read_csv("Gruenanlagen/Quelle_Geoportal_Berlin/gruenanlagen_berlin.csv")
stops_df = pd.read_csv("Haltestellen/Quelle_Openstreetmap/oepnv_02_osmnx_result.csv")
stores_df = pd.read_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")

stops_df = stops_df[stops_df["name"].notna()].copy()
stores_df = stores_df[stores_df["name"].notna()].copy()

green_spaces_df["geometry"] = green_spaces_df["geometry"].apply(wkt.loads)
stops_df["geometry"] = stops_df["geometry"].apply(wkt.loads)
stores_df["geometry"] = stores_df["geometry"].apply(wkt.loads)

fountains = gpd.read_file("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
stops = gpd.GeoDataFrame(stops_df, geometry="geometry", crs="EPSG:4326")
stores = gpd.GeoDataFrame(stores_df, geometry="geometry", crs="EPSG:4326")
green_spaces = gpd.GeoDataFrame(green_spaces_df, geometry="geometry", crs="EPSG:25833")
green_spaces = green_spaces.to_crs(epsg=4326)

# -------------------------------------------------
# Map center (Berlin)
# -------------------------------------------------
m = folium.Map(location=[52.52, 13.405], zoom_start=12, tiles="CartoDB positron")

# -------------------------------------------------
# Feature Groups (Layers)
# -------------------------------------------------
fountains_fg = folium.FeatureGroup(name="Drinking Fountains")
stops_fg = folium.FeatureGroup(name="Public Transport Stops")
stores_fg = folium.FeatureGroup(name="Beverage Stores")
green_fg = folium.FeatureGroup(name="Green Spaces")

# -------------------------------------------------
# MarkerCluster for large datasets
# -------------------------------------------------
stops_cluster = MarkerCluster().add_to(stops_fg)
stores_cluster = MarkerCluster().add_to(stores_fg)

# -------------------------------------------------
# Drinking fountains (blue markers)
# -------------------------------------------------
for _, row in fountains.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4,
        color="blue",
        fill=True,
        fill_opacity=0.8,
        popup=f"Drinking Fountain No: {row.get('trinkbrunnennummer', 'N/A')}"
    ).add_to(fountains_fg)

# -------------------------------------------------
# Public transport stops (yellow, clustered)
# -------------------------------------------------
for _, row in stops.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="yellow",
        fill=True,
        fill_opacity=0.6,
        popup=row.get("name", "Stop")
    ).add_to(stops_cluster)

# -------------------------------------------------
# Beverage stores (red, clustered)
# -------------------------------------------------
for _, row in stores.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=row.get("name", "Store")
    ).add_to(stores_cluster)

# -------------------------------------------------
# Green spaces (polygon layer)
# -------------------------------------------------
folium.GeoJson(
    green_spaces,
    name="Green Spaces",
    style_function=lambda x: {
        "fillColor": "lightgreen",
        "color": "darkgreen",
        "weight": 1,
        "fillOpacity": 0.3,
    },
    tooltip=folium.GeoJsonTooltip(fields=["namenr"], aliases=["Name:"])
).add_to(green_fg)

# -------------------------------------------------
# Add layers to map
# -------------------------------------------------
fountains_fg.add_to(m)
stops_fg.add_to(m)
stores_fg.add_to(m)
green_fg.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

file_path = "berlin_drinking_fountain_analysis.html"
m.save(file_path)

webbrowser.open('file://' + os.path.realpath(file_path))
