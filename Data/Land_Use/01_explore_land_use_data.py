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

import geopandas as gpd

filename = "flaechennutzung2022_WGS84.geojson"

gdf = gpd.read_file(filename)

# nutz → nutzung
nutz_df = (
    gdf[["nutz", "enutzung"]]
    .drop_duplicates()
    .sort_values("nutz")
)

print("\n=== 'nutz' → 'enutzung' ===")
print(nutz_df.to_string(index=False))

# typ → typklar
typ_df = (
    gdf[["typ", "etypklar"]]
    .drop_duplicates()
    .sort_values("typ")
)

print("\n=== 'typ' → 'etypklar' ===")
print(typ_df.to_string(index=False)) 
