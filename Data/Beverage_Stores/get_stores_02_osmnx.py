"""
MIT License

Copyright (c) 2026 Sabrina Otto

This file is part of this project and is licensed under the MIT License.
See the LICENSE file in the project root for the full license text.

Note on datasets:
This project uses third-party datasets from the Berlin Open Data portal
and OpenStreetMap. These datasets are not covered by the MIT License and
remain subject to their respective licenses.
"""

import osmnx as ox

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
