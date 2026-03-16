import osmnx as ox
import pandas as pd
import geopandas as gpd

# Define area
place = "Berlin, Germany"

# OSM tags for public transport stops
tags = {
    "public_transport": ["platform", "stop_position", "station"],
    "railway": ["tram_stop", "station", "halt"],
    "highway": ["bus_stop"],
    "subway": ["yes"],
    "light_rail": ["yes"],
    "ferry": ["yes"]
}

# Retrieve stops
gdf = ox.features_from_place(place, tags)

# Keep only nodes (points)
gdf = gdf[gdf.geom_type == "Point"]

# Add unique ID
gdf = gdf.reset_index()
gdf.rename(columns={'element id': 'id'}, inplace=True)

# List of relevant columns that should be included in type_info
type_columns = [
    'highway', 'railway', 'public_transport', 'station', 
    'tram', 'bus', 'subway', 'light_rail', 'ferry'
]

# Primary transport modes
primary_modes = ['bus', 'tram', 'subway', 'light_rail', 'ferry']

# Generate type_info
def generate_type_info(row):
    parts = []

    for col in type_columns:
        val = row.get(col)
        if val in [None, '', 0, False, float('nan')]:
            continue
        if str(val).lower() == 'yes':
            val_str = col
        else:
            val_str = str(val)
        parts.append(val_str)

    # Remove duplicates
    parts = list(dict.fromkeys(parts))

    # Keep only primary transport modes if present
    primary_found = [p for p in parts if p in primary_modes]

    if primary_found:
        return ", ".join(primary_found)
    elif 'station' in parts:
        return 'station'
    else:
        return None

gdf['type_info'] = gdf.apply(generate_type_info, axis=1)

# Remove duplicate stops based on the name
named = gdf[gdf["name"].notna()].drop_duplicates(subset="name")
unnamed = gdf[gdf["name"].isna()]
gdf = gpd.GeoDataFrame(pd.concat([named, unnamed], ignore_index=True))

# Optionally keep only relevant columns
gdf = gdf[['id', 'name', 'type_info', 'geometry']]

# Save as CSV
output_path = "oepnv_02_osmnx_result.csv"
gdf.to_csv(output_path, index=False)

print(f"{len(gdf)} stations were saved in '{output_path}'.")
print(gdf.head())
