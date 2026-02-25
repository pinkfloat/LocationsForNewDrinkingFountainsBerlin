 
import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
from scipy.spatial import cKDTree

# --------------------------------------------------
# 1. Change to EPSG:25833 to get distances in meter
# --------------------------------------------------

TARGET_CRS = "EPSG:25833"

def load_points_csv(path):
    df = pd.read_csv(path)
    df = df[df["name"].notna()].copy()
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf.to_crs(TARGET_CRS)

stops = load_points_csv("Haltestellen/Quelle_Openstreetmap/oepnv_02_osmnx_result.csv")
stores = load_points_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")


def load_geojson_fix_crs(path):
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs("EPSG:4326", allow_override=True)
    return gdf.to_crs(TARGET_CRS)

fountains = load_geojson_fix_crs("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
berlin_area = load_geojson_fix_crs("Flaechennutzung/berlin_area_merged.geojson")

# --------------------------------------------------
# Test
# --------------------------------------------------
# print("CRS stops:", stops.crs)
# print("CRS stores:", stores.crs)
# print("CRS fountains:", fountains.crs)
# print("CRS berlin_area:", berlin_area.crs)

# print("\nExample coordinate (Meter):")
# print(fountains.geometry.iloc[0])


# --------------------------------------------------
# 2. DISTANCE: FOUNTAINS -> STOPS
# --------------------------------------------------

def nearest_distance(source_gdf, target_gdf):
    """
    Computes the Euclidean distance (in meters) from each
    point in a source GeoDataFrame to its nearest neighbor
    in a target GeoDataFrame.

    Method:
    - Extracts projected x/y coordinates
    - Builds a cKDTree spatial index for efficient search
    - Queries the nearest neighbor (k=1)

    Returns:
    Array of minimum distances (meters)
    """
    source_coords = np.array(list(zip(source_gdf.geometry.x, source_gdf.geometry.y)))
    target_coords = np.array(list(zip(target_gdf.geometry.x, target_gdf.geometry.y)))
    
    tree = cKDTree(target_coords)
    distances, _ = tree.query(source_coords, k=1)
    
    return distances  # in meters

# Info:
# --------------------------------------------------
# Spatial Nearest Neighbor Search using cKDTree
# --------------------------------------------------
# Uses a k-dimensional tree (KDTree) data structure
# to efficiently compute nearest neighbor distances.
#
# Advantage:
# Reduces computational complexity from O(n²)
# to approximately O(n log n).
#
# Distance metric:
# Euclidean distance in projected CRS (meters).
# --------------------------------------------------

fountains["dist_to_stop"] = nearest_distance(fountains, stops)
fountains["dist_to_store"] = nearest_distance(fountains, stores)

print("Average Distance Fountain -> Stop (m):",
      fountains["dist_to_stop"].mean())

print("Average Distance Fountain -> Store (m):",
      fountains["dist_to_store"].mean())


# --------------------------------------------------
# 3. DISTANCE: FOUNTAIN -> FOUNTAIN
# --------------------------------------------------
coords = np.array(list(zip(fountains.geometry.x, fountains.geometry.y)))
tree = cKDTree(coords)

distances, indices = tree.query(coords, k=2)  
# k=2, as with k=1 the next point would be itself (distance = 0)

fountains["dist_to_nearest_fountain"] = distances[:, 1]

print("Average Distance Fountain -> Fountain (m):",
      fountains["dist_to_nearest_fountain"].mean())


# --------------------------------------------------
# 4. FOUNTAINS PER AREA (Usage Type)
# --------------------------------------------------
fountains_with_landuse = gpd.sjoin(
    fountains,
    berlin_area[["enutzung", "geometry"]],
    how="left",
    predicate="within"
)
landuse_counts = fountains_with_landuse["enutzung"].value_counts(normalize=True) * 100

print("\nDistribution of Fountains dependend on landuse (%):")
print(landuse_counts)
