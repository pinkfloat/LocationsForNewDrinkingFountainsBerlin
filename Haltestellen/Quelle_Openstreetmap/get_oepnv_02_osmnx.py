import osmnx as ox
import geopandas as gpd

# Gebiet definieren
place = "Berlin, Germany"

# OSM Tags für ÖPNV-Haltestellen
tags = {
    "public_transport": ["platform", "stop_position", "station"],
    "railway": ["tram_stop", "station", "halt"],
    "highway": ["bus_stop"],
    "subway": ["yes"],
    "light_rail": ["yes"],
    "ferry": ["yes"]
}

# Haltestellen abrufen
gdf = ox.features_from_place(place, tags)

# Nur Nodes behalten (Punkte)
gdf = gdf[gdf.geom_type == "Point"]

# Eindeutige ID hinzufügen
gdf = gdf.reset_index()
gdf.rename(columns={'element id': 'id'}, inplace=True)

# Liste der relevanten Spalten, die in type_info einfließen sollen
type_columns = [
    'highway', 'railway', 'public_transport', 'station', 
    'tram', 'bus', 'subway', 'light_rail', 'ferry'
]

# Primäre Verkehrsmittel
primary_modes = ['bus', 'tram', 'subway', 'light_rail', 'ferry']

# type_info erzeugen
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

    # Duplikate entfernen
    parts = list(dict.fromkeys(parts))

    # Nur primäre Verkehrsmittel behalten, wenn vorhanden
    primary_found = [p for p in parts if p in primary_modes]

    if primary_found:
        return ", ".join(primary_found)
    elif 'station' in parts:
        return 'station'
    else:
        return None

gdf['type_info'] = gdf.apply(generate_type_info, axis=1)

# Optional nur relevante Spalten behalten
gdf = gdf[['id', 'name', 'type_info', 'geometry']]

# Als CSV speichern
output_path = "oepnv_02_osmnx_result.csv"
gdf.to_csv(output_path, index=False)

print(f"Es wurden {len(gdf)} Stationen gespeichert in '{output_path}'.")
print(gdf.head())