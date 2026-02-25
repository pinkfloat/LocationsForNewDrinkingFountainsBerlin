 
import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import chi2_contingency

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


# --------------------------------------------------
# 5. CHI-SQUARE TEST: Fountains in green vs. non-green areas
# --------------------------------------------------
# Check whether fountains tend to be placed in green spaces:

# Research Question: Are fountains disproportionately located
# in green areas compared to the overall land-use distribution in Berlin?

# H0 (Null hypothesis):
# Fountain placement is independent of land-use type.

# H1 (Alternative hypothesis):
# Fountains are overrepresented in green areas.

# Define green land-use types
green_types = [
    "Park / green space",
    "Allotment garden",
    "Forest",
    "Sport use",
    "Fallow area, mixed vegetation - meadows, trees, bushes",
    "Cemetery",
]

# Observed distribution: Land-use of areas where fountains are located
fountains_with_landuse["is_green"] = fountains_with_landuse["enutzung"].isin(green_types)

observed_green = fountains_with_landuse["is_green"].sum()
observed_non_green = len(fountains_with_landuse) - observed_green

# Expected distribution: Land-use distribution of all Berlin areas
berlin_area["is_green"] = berlin_area["enutzung"].isin(green_types)
expected_green = berlin_area["is_green"].sum()
expected_non_green = len(berlin_area) - expected_green

contingency_table = [
    [observed_green, observed_non_green],
    [expected_green, expected_non_green]
]

# Is the proportion of fountains in green areas different from
# the proportion of green areas in Berlin overall?
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print("\nChi-Square Test Results")
print("------------------------")
print("Observed Green:", observed_green)
print("Observed Non-Green:", observed_non_green)
print("Expected Green (overall areas):", expected_green)
print("Expected Non-Green (overall areas):", expected_non_green)
print("\nChi2 statistic:", chi2)
print("p-value:", p_value)
print("Degrees of freedom:", dof)

# Effect size:
n = np.sum(contingency_table)
cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.__len__()-1, 1))))

print("Cramér's V:", cramers_v)

# Proportion:
# Share of green areas in Berlin: 7573 / (7573 + 18849) = 0.2866
# Share of fountains in green areas: 53 / (53 + 189) = 0.2190

# Result: Fountains are actually underrepresented in green areas
# relative to their overall availability.
# (Even though "Park / green space" alone got approx. 43% of all fountains.)

# This is likely because forest areas and cemeteries etc. tend to go without fountains...
