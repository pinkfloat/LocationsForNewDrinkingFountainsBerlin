import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
from shapely.geometry import Point
from shapely.ops import nearest_points

# ==============================
# GENERAL SETTINGS
# ==============================
TARGET_CRS = "EPSG:25833"

# ==============================
# LOAD DATASETS
# ==============================
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

# ==============================
# PARAMETERS
# ==============================
N_NEW_FOUNTAINS = 50
MIN_DISTANCE_NEW = 2000  # meters between newly created fountains
URBAN_RADIUS = 3000  # meters for urban population context

weights = {
    "landuse": 0.50,
    "population": 0.10,
    "urban_pop": 0.40,
    "dist_fountain": 0.50,
    "dist_store": 0.15,
    "dist_stop": 0.10,
    "edge": 0.01,
}

# Land use base suitability scores
landuse_scores = {
    130: 0.9,  # Park / green space
    190: 0.9,  # Sport use
    140: 0.8,  # City square
    10: 0.8,   # Housing area
    30: 0.6,   # Core area
    21: 0.6,   # Mixed area
    50: 0.5,   # Public use
    100: 0.3,  # Forest
}

# Excluded land uses
# nutz                                               enutzung                                                    nutzung
#  110                                          Body of water                                                   Gewässer
#  122                                               Farmland                                                  Ackerland
#  160                                       Allotment garden                                          Kleingartenanlage
#  200                            Tree nursery / horticulture                                     Baumschule / Gartenbau
#   40                         Commercial and industrial area  Gewerbe- und Industrienutzung, großflächiger Einzelhandel
#   60                                           Utility area                                        Ver- und Entsorgung
#   70           Weekend cottage / allotment-garden-type area             Wochenendhaus- und kleingartenähnliche Nutzung
#   80                           Traffic area (without roads)                              Verkehrsfläche (ohne Straßen)
#   90                                      Construction site                                                  Baustelle

excluded_landuse = [110, 122, 160, 200, 40, 60, 70, 80, 90]


# ==============================
# HELPER FUNCTIONS
# ==============================
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def inverse_normalize(series):
    norm = normalize(series)
    return 1 - norm

def compute_min_distance(source_gdf, target_gdf):
    return source_gdf.geometry.apply(
        lambda geom: target_gdf.distance(geom).min()
    )

def population_in_radius(point, polygons, radius):
    buffer = point.buffer(radius)
    nearby = polygons[polygons.intersects(buffer)]
    return nearby["ew2023"].sum()

# ==============================
# PREPARE POLYGONS
# ==============================
# Remove excluded land use
berlin_area = berlin_area[~berlin_area["nutz"].isin(excluded_landuse)].copy()

# Save polygon boundary before next line for city border calculation
berlin_boundary = berlin_area.geometry.union_all()

# Generate centroid candidate points
berlin_area["geometry"] = berlin_area.centroid

# Remove polygons without population
berlin_area = berlin_area[berlin_area["ew_ha_2023"] > 0].copy()

# ==============================
# URBAN POPULATION CONTEXT
# ==============================
berlin_area["urban_pop_raw"] = berlin_area.geometry.apply(
    lambda g: population_in_radius(g, berlin_area, URBAN_RADIUS)
)

# ==============================
# DISTANCE CALCULATIONS
# ==============================
berlin_area["dist_fountain"] = compute_min_distance(berlin_area, fountains)
berlin_area["dist_store"] = compute_min_distance(berlin_area, stores)
berlin_area["dist_stop"] = compute_min_distance(berlin_area, stops)

# Distance to city border
berlin_area["dist_edge"] = berlin_area.distance(berlin_boundary.boundary)

# ==============================
# NORMALIZATION
# ==============================
# High area population, and high distances to other fountains and stores = good
# Low distance to stops = good (thus inverse) 
berlin_area["score_population"] = normalize(berlin_area["ew_ha_2023"])
berlin_area["score_dist_fountain"] = normalize(berlin_area["dist_fountain"])
berlin_area["score_dist_store"] = normalize(berlin_area["dist_store"])
berlin_area["score_dist_stop"] = inverse_normalize(berlin_area["dist_stop"])

# Urban population context -> Areas with many residents around = also good
berlin_area["score_urban_pop"] = normalize(berlin_area["urban_pop_raw"])

# Polishing: Penalize putting new fountains at city border
berlin_area["edge_score"] = normalize(berlin_area["dist_edge"])

# ==============================
# LAND USE SCORING
# ==============================
# Apply landuse scores, otherwise use 0.2 as default
def compute_landuse_score(row):
    base = landuse_scores.get(row["nutz"], 0.2)

    # Bonus: Park without existing fountain inside
    if row["nutz"] == 130:
        park_polygon = row.geometry.buffer(10)
        if fountains.within(park_polygon).sum() == 0:
            base += 0.2

    return min(base, 1.0)

berlin_area["score_landuse"] = berlin_area.apply(compute_landuse_score, axis=1)

# ==============================
# WEIGHTED LINEAR COMBINATION
# ==============================
berlin_area["final_score"] = (
    weights["landuse"] * berlin_area["score_landuse"] +
    weights["population"] * berlin_area["score_population"] +
    weights["urban_pop"] * berlin_area["score_urban_pop"] +
    weights["dist_fountain"] * berlin_area["score_dist_fountain"] +
    weights["dist_store"] * berlin_area["score_dist_store"] +
    weights["dist_stop"] * berlin_area["score_dist_stop"] +
    weights["edge"] * berlin_area["edge_score"]
)

# ==============================
# GREEDY SELECTION WITH DISTANCE CONSTRAINT
# ==============================
selected_points = []
selected_geometries = []

sorted_candidates = berlin_area.sort_values("final_score", ascending=False)

for idx, row in sorted_candidates.iterrows():

    candidate_geom = row.geometry

    if len(selected_geometries) == 0:
        selected_points.append(row)
        selected_geometries.append(candidate_geom)
    else:
        distances = [candidate_geom.distance(g) for g in selected_geometries]
        if min(distances) >= MIN_DISTANCE_NEW:
            selected_points.append(row)
            selected_geometries.append(candidate_geom)

    if len(selected_points) >= N_NEW_FOUNTAINS:
        break


# ==============================
# OUTPUT GEO DATAFRAME
# ==============================
new_fountains = gpd.GeoDataFrame(selected_points, geometry="geometry", crs=berlin_area.crs).copy()
new_fountains = new_fountains.reset_index(drop=True)
new_fountains["nummer"] = new_fountains.index + 1

new_fountains = new_fountains[["nummer", "geometry"]]

new_fountains_wgs84 = new_fountains.to_crs("EPSG:4326")
print(new_fountains_wgs84.head())
new_fountains_wgs84.to_file("new_calculated_fountains.geojson", driver="GeoJSON")
