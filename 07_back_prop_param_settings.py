import geopandas as gpd
import pandas as pd
from shapely import wkt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import json
import itertools

# ==============================
# GENERAL SETTINGS
# ==============================
TARGET_CRS = "EPSG:25833"
N_NEW_FOUNTAINS = 50

MIN_DISTANCE_RANGE = [500, 600, 700, 800, 900, 1000]
URBAN_RADIUS_RANGE = [500, 600, 700, 800, 900, 1000]

EPOCHS = 500

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
# CONST. PARAMETERS
# ==============================
# These parameters ain't changed as it would take forever...

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
    min_val = series.min()
    max_val = series.max()
    denom = max_val - min_val
    
    if denom == 0:
        return pd.Series(0, index=series.index)

    return (series - min_val) / denom

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
# MODEL
# ==============================
class FountainModel(nn.Module):

    def __init__(self):
        super().__init__()
        self.weights = nn.Parameter(torch.rand(6))

    def forward(self, x):
        w = torch.softmax(self.weights, dim=0)
        scores = (x * w).sum(dim=1)
        probs = torch.softmax(scores, dim=0)
        return probs

# ==============================
# PLACEMENT MODEL
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

    for _, row in sorted_candidates.iterrows():
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

    return gpd.GeoDataFrame(
        selected, geometry="geometry", crs=temp.crs
    )

# ==============================
# EVALUATION
# ==============================
def evaluate_model(predicted):
    distances = predicted.geometry.apply(
        lambda geom: fountains.distance(geom).min()
    )
    return distances.mean()

# ==============================
# MAIN LOOP
# ==============================
results = []

print("Starting optimization...")

for MIN_DISTANCE_NEW, URBAN_RADIUS in itertools.product(
    MIN_DISTANCE_RANGE,
    URBAN_RADIUS_RANGE
):
    print("\nTesting:", MIN_DISTANCE_NEW, URBAN_RADIUS)
    temp = berlin_area.copy()

    # urban population
    temp["urban_pop_raw"] = temp.geometry.apply(
        lambda g: population_in_radius(g, berlin_area, URBAN_RADIUS)
    )

    temp["score_urban_pop"] = normalize(temp["urban_pop_raw"])

    feature_cols = [
        "score_landuse",
        "score_population",
        "score_urban_pop",
        "score_dist_store",
        "score_dist_stop",
        "edge_score",
    ]

    features = torch.tensor(
        temp[feature_cols].values,
        dtype=torch.float32
    )

    coords = torch.tensor(
        np.array([[g.x, g.y] for g in temp.geometry]),
        dtype=torch.float32
    )

    real_coords = torch.tensor(
        np.array([[g.x, g.y] for g in fountains.geometry]),
        dtype=torch.float32
    )

    def loss_fn(probs):
        diff = coords[:, None, :] - real_coords[None, :, :]
        dists = torch.sqrt((diff ** 2).sum(dim=2) + 1e-8)
        min_dists, _ = torch.min(dists, dim=1)

        # normalize distances
        min_dists = min_dists / 10000.0

        return (probs * min_dists).sum()

    model = FountainModel()
    optimizer = optim.Adam(model.parameters(), lr=0.05)

    for epoch in range(EPOCHS):
        optimizer.zero_grad()
        probs = model(features)
        loss = loss_fn(probs)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    with torch.no_grad():
        learned = torch.softmax(model.weights,dim=0).numpy()

    weights = {
        "landuse": float(learned[0]),
        "population": float(learned[1]),
        "urban_pop": float(learned[2]),
        "dist_store": float(learned[3]),
        "dist_stop": float(learned[4]),
        "edge": float(learned[5]),
    }

    predicted = run_fountain_model(temp, weights, MIN_DISTANCE_NEW)
    score = evaluate_model(predicted)

    results.append({
        "score": float(score),
        "weights": weights,
        "MIN_DISTANCE_NEW": MIN_DISTANCE_NEW,
        "URBAN_RADIUS": URBAN_RADIUS
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
with open( "fountain_backprop_results.json", "w") as f:
    json.dump(results_sorted, f, indent=4)

print("Saved results.") 
