import osmnx as ox
import geopandas as gpd

place = "Berlin, Germany"
tags = {"leisure": "park"}

# Name (so vorhanden) und Geometrien eines Parks extrahieren
gdf = ox.features_from_place(place, tags=tags)
gdf = gdf[['name', 'geometry']] if 'name' in gdf.columns else gdf[['geometry']]

# EPSG:4326 = WGS84, also Latitude / Longitude
gdf = gdf.to_crs(epsg=4326)

# Flaeche berechnen
# Um Flächen in Quadratmetern zu berechnen, muss das CRS meterbasiert sein.
# EPSG:3857 = Web Mercator (Meter statt Grad).
# .area gibt die Fläche der Polygone in Quadratmetern.
gdf['area_m2'] = gdf['geometry'].to_crs(epsg=3857).area

# Eindeutige ID hinzufügen
gdf = gdf.reset_index()
gdf.rename(columns={'element id': 'id'}, inplace=True)

# Als CSV speichern
output_path = "gruenanlagen_02_osmnx_result.csv"
gdf.to_csv(output_path, index=False)

print(f"Es wurden {len(gdf)} Parks gespeichert in '{output_path}'.")
print(gdf.head())