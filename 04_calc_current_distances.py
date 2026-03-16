 
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

stops = load_points_csv("Haltestellen/oepnv_02_osmnx_result.csv")
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



# Adjustment:
# 1. Compare for different green area types
# 2. Compare fountain vs. non-fountain areas instead of
#    fountain vs. all berlin areas.

def chi_square_green_test(fountains_gdf, berlin_area_gdf, green_types):
    """
    Performs a Chi-Square test of independence to evaluate whether
    fountains are disproportionately located in specified land-use types.

    Additionally prints:
    - Share of fountain areas that are green
    - Share of all areas that are green
    - Probability of fountain given green vs non-green
    - Relative risk
    """

    # Make a copy to avoid modifying original dataframe
    berlin_area_gdf = berlin_area_gdf.copy()

    # --------------------------------------------------
    # 1. Spatial join: determine which areas contain fountains
    # --------------------------------------------------
    joined = gpd.sjoin(
        berlin_area_gdf,
        fountains_gdf[["geometry"]],
        how="left",
        predicate="contains"
    )

    # Area has fountain if at least one match exists
    joined["has_fountain"] = ~joined.index_right.isna()

    # If multiple fountains fall into same polygon,
    # reduce to unique polygons
    area_status = joined.groupby(joined.index).agg({
        "has_fountain": "max"
    })

    # Merge back to original berlin_area
    berlin_area_gdf = berlin_area_gdf.join(area_status)

    berlin_area_gdf["has_fountain"] = berlin_area_gdf["has_fountain"].fillna(False)

    # Debugging:
    # print(berlin_area_gdf.head())

    # --------------------------------------------------
    # 2. Classify green vs non-green
    # --------------------------------------------------
    berlin_area_gdf["is_green"] = berlin_area_gdf["enutzung"].isin(green_types)

    # --------------------------------------------------
    # 3. Build contingency table
    # --------------------------------------------------
    fountain_green = berlin_area_gdf[
        (berlin_area_gdf["has_fountain"]) &
        (berlin_area_gdf["is_green"])
    ].shape[0]

    fountain_non_green = berlin_area_gdf[
        (berlin_area_gdf["has_fountain"]) &
        (~berlin_area_gdf["is_green"])
    ].shape[0]

    no_fountain_green = berlin_area_gdf[
        (~berlin_area_gdf["has_fountain"]) &
        (berlin_area_gdf["is_green"])
    ].shape[0]

    no_fountain_non_green = berlin_area_gdf[
        (~berlin_area_gdf["has_fountain"]) &
        (~berlin_area_gdf["is_green"])
    ].shape[0]

    contingency_table = [
        [fountain_green, fountain_non_green],
        [no_fountain_green, no_fountain_non_green]
    ]

    # --------------------------------------------------
    # 4. Chi-Square Test
    # --------------------------------------------------
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    # --------------------------------------------------
    # 5. Effect Size (Cramér's V)
    # --------------------------------------------------
    n = np.sum(contingency_table)
    cramers_v = np.sqrt(chi2 / (n * (min(len(contingency_table)-1, 
                                         len(contingency_table[0])-1))))

    # --------------------------------------------------
    # 6. Proportions
    # --------------------------------------------------
    total_areas = berlin_area_gdf.shape[0]
    total_fountain_areas = fountain_green + fountain_non_green
    total_green_areas = fountain_green + no_fountain_green

    share_fountain_green = fountain_green / total_fountain_areas
    share_green_overall = total_green_areas / total_areas

    # Probability of fountain given green vs non-green
    prob_fountain_given_green = fountain_green / total_green_areas
    prob_fountain_given_non_green = (
        fountain_non_green /
        (fountain_non_green + no_fountain_non_green)
    )

    # Relative Risk
    relative_risk = prob_fountain_given_green / prob_fountain_given_non_green

    # --------------------------------------------------
    # 7. Print results
    # --------------------------------------------------
    print("\nChi-Square Test Results")
    print("------------------------")
    print("Contingency Table:")
    print(np.array(contingency_table))

    print("\nChi2 statistic:", chi2)
    print("p-value:", p_value)
    print("Degrees of freedom:", dof)
    print("Cramér's V:", cramers_v)

    print("\n--- Proportions ---")
    print("Share of fountain areas that are green:",
          round(share_fountain_green, 4))
    print("Share of green areas overall:",
          round(share_green_overall, 4))

    print("\nProbability of fountain given green:",
          round(prob_fountain_given_green, 6))
    print("Probability of fountain given non-green:",
          round(prob_fountain_given_non_green, 6))

    print("\nRelative Occurence / Risk (green vs non-green):",
          round(relative_risk, 3))

    return {
        "chi2": chi2,
        "p_value": p_value,
        "dof": dof,
        "cramers_v": cramers_v,
        "relative_risk": relative_risk,
        "contingency_table": contingency_table
    }

print("\n\nFirst Test: All green areas (like before)")
chi_square_green_test(fountains, berlin_area, green_types)

# Result: Although green areas represent only ~29% of all land-use polygons, they contain ~52% of fountain areas.
# That is a strong descriptive overrepresentation (2.65 times more).
# The association is statistically significant. (p value in e-6)
# However, the effect size is small.(Cremer value is 0.03 which is < 0.1, as areas with fountains are undersampled)

print("\n\nSecond Test: Only Parks")
chi_square_green_test(fountains, berlin_area, ["Park / green space"])

# Result: Parks make up only ~9% of Berlin’s land-use polygons, but they contain 42% of fountain areas.
# That is a very strong concentration (7.45 times more).
# Extremely statistically significan (p value in e-29)
# With Cremer V. ~= 0.07 still considered a "small" effect statistically - but at least stronger than 0.03.

# Final Result: Fountains function as amenity infrastructure rather than general environmental infrastructure.
# (They are a nice-to-have, but not essential ... and don't work in winter months anyways.)
