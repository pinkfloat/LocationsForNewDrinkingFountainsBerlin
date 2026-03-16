import pandas as pd
import geopandas as gpd
from shapely import wkt

# -------------------------------------------------
# Display settings
# -------------------------------------------------
pd.set_option('display.max_columns', None)

# -------------------------------------------------
# Load CSV Data
# -------------------------------------------------
stops_df = pd.read_csv("Haltestellen/oepnv_02_osmnx_result.csv")
stores_df = pd.read_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")

# Load GeoJSON Data
fountains = gpd.read_file("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
berlin_area = gpd.read_file("Flaechennutzung/berlin_area_merged.geojson")

# -------------------------------------------------
# Keep only entries with names
# -------------------------------------------------
stops_df = stops_df[stops_df["name"].notna()].copy()
stores_df = stores_df[stores_df["name"].notna()].copy()

# -------------------------------------------------
# Convert WKT to geometry (CSV only)
# -------------------------------------------------
stops_df["geometry"] = stops_df["geometry"].apply(wkt.loads)
stores_df["geometry"] = stores_df["geometry"].apply(wkt.loads)

# -------------------------------------------------
# Convert to GeoDataFrame (correct CRS)
# -------------------------------------------------
stops = gpd.GeoDataFrame(
    stops_df,
    geometry="geometry",
    crs="EPSG:4326"
)

stores = gpd.GeoDataFrame(
    stores_df,
    geometry="geometry",
    crs="EPSG:4326"
)

# -------------------------------------------------
# FIX CRS for GeoJSON (wrongly tagged as 25833)
# -------------------------------------------------
# 13.41 , 52.43 Degree instead of 392000 , 5810000 Meters = WGS84
print("Sample Fountain coords:", fountains.geometry.iloc[0])
print("Sample Area coords:", berlin_area.geometry.iloc[0])
fountains = fountains.set_crs("EPSG:4326", allow_override=True)
berlin_area = berlin_area.set_crs("EPSG:4326", allow_override=True)

# -------------------------------------------------
# Print number of objects
# -------------------------------------------------
print("\nNum Fountains:", len(fountains))
print("Num Stops:", len(stops))
print("Num Stores:", len(stores))
print("Num Areas:", len(berlin_area))

# -------------------------------------------------
# Final CRS Check
# -------------------------------------------------
print("\nCRS Check:")
print("Fountains:", fountains.crs)
print("Stops:", stops.crs)
print("Stores:", stores.crs)
print("Berlin Areas:", berlin_area.crs)
