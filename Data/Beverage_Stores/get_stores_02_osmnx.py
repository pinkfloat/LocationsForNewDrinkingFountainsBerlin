import osmnx as ox
import geopandas as gpd

place_name = "Berlin, Germany"

# --------------------------------
# 1. Relevante POIs laden
# --------------------------------
tags = {
    "shop": ["supermarket", "convenience", "kiosk"],
    "amenity": ["fast_food", "fuel"]
}

pois = ox.features_from_place(place_name, tags)

# --------------------------------
# 2. Nur Polygon- und Punkt-Geometrien behalten
# --------------------------------
pois = pois[
    pois.geometry.type.isin(["Polygon", "MultiPolygon", "Point"])
].copy()

# OSM-ID extrahieren
pois["id"] = pois.index.get_level_values(1)

# --------------------------------
# 3. Projektion für korrekte Centroid-Berechnung
# --------------------------------
pois_proj = ox.projection.project_gdf(pois)

# Nur bei Polygonen Centroid berechnen
pois_proj["geometry"] = pois_proj.geometry.centroid

# Zurück nach WGS84
pois_centroids = pois_proj.to_crs(epsg=4326)

# --------------------------------
# 4. Ausgabe vorbereiten
# --------------------------------
result = pois_centroids[["id", "name", "geometry"]].copy()

# Als CSV speichern
output_path = "stores_02_osmnx_result.csv"
result.to_csv(output_path, index=False)

print(f"Es wurden {len(result)} Stores gespeichert in '{output_path}'.")
print(result.head())
