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

# -----------------------------
# Choose row number to compare entries
# -----------------------------
row = 12

# -----------------------------
# Load data
# -----------------------------
usage_df = gpd.read_file("flaechennutzung2022_WGS84.geojson")
population_df = gpd.read_file("einwohnerdichte2023_WGS84.geojson")

# Check if index exists
if row >= len(usage_df):
    raise IndexError(f"Row {row} doesn't exist. DataFrame only has {len(usage_df)} rows.")

# -----------------------------
# Print row of usage_df
# -----------------------------
usage_row = usage_df.iloc[row]

print("\n--- usage_df row ---")
print(usage_row)

# -----------------------------
# Take key of this row
# -----------------------------
schluessel = usage_row["schluessel"]
print(f"\nkey: {schluessel}")

# -----------------------------
# Print corresponding row of population_df
# -----------------------------
matching_population_row = population_df[population_df["schluessel"] == schluessel]

if matching_population_row.empty:
    print("\nKey doesn't exist in population_df.")
else:
    print("\n--- population_df corresponding row ---")
    print(matching_population_row.iloc[0])
