import pandas as pd
import geopandas as gpd
import requests
from osm2geojson import json2geojson

# Overpass-Abfrage definieren
OVERPASS_URL = "http://overpass-api.de/api/interpreter"

# Ways
# Eine geordnete Liste von Knotenpunkten, die Linien oder Polygone bilden.
# Beispiel: Die Umrandung eines Parks, ein Gehweg, eine Straße.

# Relations
# Eine Sammlung von Knoten, Ways und/oder anderen Relationen, die eine komplexe Struktur repräsentieren.
# Beispiel: Ein großer Park, der aus mehreren Polygonen (z.B. Wiesen, Teiche) besteht.

# Anfragen an die Overpass-API senden und in GeoJSON umwandeln
def fetch_osm_geodata(feature_type: str) -> gpd.GeoDataFrame:
    """
    Lädt OSM-Geodaten eines bestimmten Typs (z.B. 'way', 'relation', 'node')
    aus der Overpass API und gibt sie als GeoDataFrame zurück.

    :param feature_type: 'way', 'relation' oder 'node'
    :return: GeoDataFrame mit Spalten ['id', 'name', 'geometry']
    """
    # Abfrage dynamisch zusammenbauen
    query = f"""
    [out:json][timeout:60];
    area["name"="Berlin"]["boundary"="administrative"];
    (
      {feature_type}["leisure"="park"](area);
    );
    out body;
    >;
    out skel qt;
    """

    # Anfrage senden
    response = requests.post(OVERPASS_URL, data={'data': query})
    data = response.json()

    # In GeoJSON umwandeln
    geojson = json2geojson(data)
    gdf = gpd.GeoDataFrame.from_features(geojson['features'])

    print(f"{len(gdf)} Einträge vom Typ '{feature_type}' wurden geladen.")
    return gdf


# Parks als Ways und Relations abrufen und kombinieren
gdf_ways = fetch_osm_geodata("way")
gdf_relations = fetch_osm_geodata("relation")

gdf = pd.concat([gdf_relations, gdf_ways], ignore_index=True)


# Name aus dem Dictionary-Feld "tags" extrahieren
def extract_name(tags):
    if isinstance(tags, dict):
        return tags.get('name', None)
    return None

gdf['name'] = gdf['tags'].apply(extract_name)

# Nur relevante Spalten behalten und neu anordnen
gdf = gdf[['id', 'name', 'geometry']]

# Als CSV speichern
output_path = "gruenanlagen_01_overpass_result.csv"
gdf.to_csv(output_path, index=False)

print(f"Es wurden {len(gdf)} Parks gespeichert in '{output_path}'.")
print(gdf.head())
