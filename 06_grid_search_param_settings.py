import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
import itertools
import json

# Idea of this script:
# Finding the most suitable parameters for the weights for script 05_calc_new_fountains_wlc.py  
# If we set the weight for "distance to already existing fountains" to zero, so that we allow
# new fountains to be placed exactly where already existing fountains are, we can try to find
# a combination of other settings, that would set the 50 new fountains as close as possible to some
# of the existing 240-something fountains. (So we are looking for a result with the minimum
# distance to them.) The combination of settings that hits the locations the best will then be stored.

# ==============================
# GENERAL SETTINGS
# ==============================
TARGET_CRS = "EPSG:25833"
N_NEW_FOUNTAINS = 50

# Grid search ranges
weight_range = [0.1, 0.3, 0.5, 0.7]
edge_range = [0.01, 0.02]

distance_range = list(range(500, 3001, 500))   # 500 → 3000
urban_radius_range = list(range(500, 3001, 500))

# ==============================
# LOAD & CLEAN DATASETS
# ==============================
def load_points_csv(path):
    df = pd.read_csv(path)
    df = df[df["name"].notna()].copy()
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf.to_crs(TARGET_CRS)

stops = load_points_csv("Haltestellen/oepnv_02_osmnx_result.csv")
stores = load_points_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")

def load_geojson_fix_crs(path):
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs("EPSG:4326", allow_override=True)
    return gdf.to_crs(TARGET_CRS)

fountains = load_geojson_fix_crs("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
berlin_area = load_geojson_fix_crs("Flaechennutzung/berlin_area_merged.geojson")

# ==============================
# CONST. PARAMETERS
# ==============================
# These parameters ain't changed during the grid search as it would take forever...

# Land use base suitability scores
landuse_scores = {
    130: 0.9,  # Park / green space
    190: 0.7,  # Sport use
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
# DISTANCE CALCULATIONS
# ==============================
berlin_area["dist_store"] = compute_min_distance(berlin_area, stores)
berlin_area["dist_stop"] = compute_min_distance(berlin_area, stops)

# Distance to city border
berlin_area["dist_edge"] = berlin_area.distance(berlin_boundary.boundary)

# ==============================
# NORMALIZATION
# ==============================
# High area population, high distances to stores and city border = good
# Low distance to stops = good (thus inverse) 
berlin_area["score_population"] = normalize(berlin_area["ew_ha_2023"])
berlin_area["score_dist_store"] = normalize(berlin_area["dist_store"])
berlin_area["score_dist_stop"] = inverse_normalize(berlin_area["dist_stop"])
berlin_area["edge_score"] = normalize(berlin_area["dist_edge"])

# ==============================
# LAND USE SCORING
# ==============================
# Shorter now, as we don't penalize parks with existing fountains
def compute_landuse_score(row):
    return landuse_scores.get(row["nutz"], 0.2)

berlin_area["score_landuse"] = berlin_area.apply(compute_landuse_score, axis=1)

# ==============================
# MODEL: Get 50 new fountain locations
# ==============================
def run_fountain_model(area_df, weights, MIN_DISTANCE_NEW):

    temp = area_df.copy()

    temp["final_score"] = (
        weights["landuse"] * temp["score_landuse"] +
        weights["population"] * temp["score_population"] +
        weights["urban_pop"] * temp["score_urban_pop"] +
        weights["dist_store"] * temp["score_dist_store"] +
        weights["dist_stop"] * temp["score_dist_stop"] +
        weights["edge"] * temp["edge_score"]
    )

    selected = []
    geometries = []

    sorted_candidates = temp.sort_values("final_score", ascending=False)

    for idx, row in sorted_candidates.iterrows():

        geom = row.geometry

        if len(geometries) == 0:
            selected.append(row)
            geometries.append(geom)

        else:
            distances = [geom.distance(g) for g in geometries]

            if min(distances) >= MIN_DISTANCE_NEW:
                selected.append(row)
                geometries.append(geom)

        if len(selected) >= N_NEW_FOUNTAINS:
            break

    return gpd.GeoDataFrame(selected, geometry="geometry", crs=temp.crs)

# ==============================
# MODEL EVALUATION
# ==============================
# for each predicted fountain:
#     compute distance to all real fountains
#     return mean of all min distances
def evaluate_model(predicted):
    distances = predicted.geometry.apply(
        lambda geom: fountains.distance(geom).min()
    )
    return distances.mean()

# ==============================
# GRID SEARCH
# ==============================
results = []

print("Starting grid search...")

for landuse, pop, urban, store, stop, edge, mindist, uradius in itertools.product(
    [0.1, 0.3, 0.5, 0.7],   # landuse weights
    [0.1, 0.3, 0.5, 0.7],   # population in this specific square weights
    [0.1, 0.3, 0.5, 0.7],   # urban population weights
    [0.1, 0.3, 0.5, 0.7],   # distance to stores weights
    [0.1, 0.3, 0.5],        # distance to stops weights
    [0.01],                 # edge weights
    [500, 1000, 2000],      # distance to other new fountains (meter)
    [500, 1000, 2000],      # span of urban population radius (meter)
):

    print("Testing:", landuse, pop, urban, store, stop, edge, mindist, uradius)

    temp = berlin_area.copy()

    # calc urban population context
    temp["urban_pop_raw"] = temp.geometry.apply(
        lambda g: population_in_radius(g, berlin_area, uradius)
    )
    temp["score_urban_pop"] = normalize(temp["urban_pop_raw"])

    weights = {
        "landuse": landuse,
        "population": pop,
        "urban_pop": urban,
        "dist_store": store,
        "dist_stop": stop,
        "edge": edge
    }

    predicted = run_fountain_model(temp, weights, mindist)

    score = evaluate_model(predicted)

    results.append({
        "score": score,
        "weights": weights,
        "MIN_DISTANCE_NEW": mindist,
        "URBAN_RADIUS": uradius
    })

# ==============================
# SORT RESULTS
# ==============================
results_sorted = sorted(results, key=lambda x: x["score"])

best = results_sorted[0]

print("\nBEST PARAMETER SET:")
print(best)

# ==============================
# SAVE RESULTS
# ==============================
with open("fountain_grid_search_results.json", "w") as f:
    json.dump(results_sorted, f, indent=4)

print("Saved results to fountain_grid_search_results.json")
