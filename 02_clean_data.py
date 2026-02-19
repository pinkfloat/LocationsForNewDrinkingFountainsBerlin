import pandas as pd
import geopandas as gpd
from shapely import wkt

# -------------------------------------------------
# Display settings
# -------------------------------------------------
pd.set_option('display.max_columns', None)

# -------------------------------------------------
# Load CSV-Data
# -------------------------------------------------
green_spaces_df = pd.read_csv("Gruenanlagen/Quelle_Geoportal_Berlin/gruenanlagen_berlin.csv")
stops_df = pd.read_csv("Haltestellen/Quelle_Openstreetmap/oepnv_02_osmnx_result.csv")
stores_df = pd.read_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")

# -------------------------------------------------
# Only keep entries with names (Stops & Stores)
# -------------------------------------------------
stops_df = stops_df[stops_df["name"].notna()].copy()
stores_df = stores_df[stores_df["name"].notna()].copy()

# -------------------------------------------------
# Geometry-Column from WKT → real Geometry
# -------------------------------------------------
green_spaces_df["geometry"] = green_spaces_df["geometry"].apply(wkt.loads)
stops_df["geometry"] = stops_df["geometry"].apply(wkt.loads)
stores_df["geometry"] = stores_df["geometry"].apply(wkt.loads)

# -------------------------------------------------
# Transform to GeoDataFrames + set CRS
# -------------------------------------------------

# Drinking Fountains (already gpd)
fountains = gpd.read_file("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")

# Stops (OSMNX -> already 4326)
stops = gpd.GeoDataFrame(
    stops_df,
    geometry="geometry",
    crs="EPSG:4326"
)

# Stores (already set to 4326 in download script)
stores = gpd.GeoDataFrame(
    stores_df,
    geometry="geometry",
    crs="EPSG:4326"
)

# Green Spaces (Saved as EPSG:25833)
green_spaces = gpd.GeoDataFrame(
    green_spaces_df,
    geometry="geometry",
    crs="EPSG:25833"
)

# Change to crs for web map
green_spaces = green_spaces.to_crs(epsg=4326)

# -------------------------------------------------
# Print number of objects
# -------------------------------------------------
print("Num Fountains:", len(fountains))
print("Num Stops:", len(stops))
print("Num Stores:", len(stores))
print("Num Green Spaces:", len(green_spaces))

# -------------------------------------------------
# Check CRS
# -------------------------------------------------
print("\nCRS Check:")
print("Fountains:", fountains.crs)
print("Stops:", stops.crs)
print("Stores:", stores.crs)
print("Green Spaces:", green_spaces.crs)
