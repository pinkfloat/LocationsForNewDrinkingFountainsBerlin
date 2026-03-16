import osmnx as ox
import geopandas as gpd

place_name = "Berlin, Germany"

# --------------------------------
# 1. Load relevant POIs
# --------------------------------
tags = {
    "shop": ["supermarket", "convenience", "kiosk"],
    "amenity": ["fast_food", "fuel"]
}

pois = ox.features_from_place(place_name, tags)

# --------------------------------
# 2. Keep only polygon and point geometries
# --------------------------------
pois = pois[
    pois.geometry.type.isin(["Polygon", "MultiPolygon", "Point"])
].copy()

# Extract OSM ID
pois["id"] = pois.index.get_level_values(1)

# --------------------------------
# 3. Projection for correct centroid calculation
# --------------------------------
pois_proj = ox.projection.project_gdf(pois)

# Calculate centroid only for polygons
pois_proj["geometry"] = pois_proj.geometry.centroid

# Back to WGS84
pois_centroids = pois_proj.to_crs(epsg=4326)

# --------------------------------
# 4. Prepare output
# --------------------------------
result = pois_centroids[["id", "name", "geometry"]].copy()

# Save as CSV
output_path = "stores_02_osmnx_result.csv"
result.to_csv(output_path, index=False)

print(f"{len(result)} stores were saved in '{output_path}'.")
print(result.head())
