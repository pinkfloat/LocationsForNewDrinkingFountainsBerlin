import geopandas as gpd
import requests
from osm2geojson import json2geojson

# Overpass-Abfrage definieren
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:50];
rel["name"="Berlin"]["type"="boundary"]["boundary"="administrative"];
map_to_area->.searchArea;
(
  node["public_transport"~"platform|stop_position|station"](area.searchArea);
  node["railway"~"tram_stop|station|halt"](area.searchArea);
  node["highway"="bus_stop"](area.searchArea);
  node["subway"="yes"](area.searchArea);
  node["light_rail"="yes"](area.searchArea);
  node["ferry"="yes"](area.searchArea);
);
out body;
>;
out skel qt;
"""

# Anfrage an die Overpass-API senden
response = requests.post(overpass_url, data={'data': overpass_query})
data = response.json()

# In GeoJSON umwandeln
geojson = json2geojson(data)
gdf = gpd.GeoDataFrame.from_features(geojson['features'])

# Name aus dem Dictionary-Feld "tags" extrahieren
def extract_name(tags):
    if isinstance(tags, dict):
        return tags.get('name', None)
    return None

gdf['name'] = gdf['tags'].apply(extract_name)

def extract_type_info(tags):
    """
    Extrahiert primäre Verkehrsmittel:
    bus, tram, subway, light_rail, ferry
    station nur, wenn kein primäres Verkehrsmittel vorhanden
    """
    if not isinstance(tags, dict):
        return None

    primary_modes = ['bus', 'tram', 'subway', 'light_rail', 'ferry']
    parts = []

    # Grundtypen
    for key in ['highway', 'railway', 'public_transport', 'station', 'ferry']:
        val = tags.get(key)
        if val not in [None, '', 'bus_stop', 'stop', 'stop_position']:
            parts.append(val)

    # Verkehrsmittel-Indikatoren
    for mode in primary_modes:
        if tags.get(mode) == 'yes':
            parts.append(mode)

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

gdf['type_info'] = gdf['tags'].apply(extract_type_info)

# Nur relevante Spalten behalten und neu anordnen
gdf = gdf[['id', 'name', 'type_info', 'geometry']]

# Als CSV speichern
output_path = "oepnv_01_overpass_result.csv"
gdf.to_csv(output_path, index=False)

print(f"Es wurden {len(gdf)} Stationen gespeichert in '{output_path}'.")
print(gdf.head())
