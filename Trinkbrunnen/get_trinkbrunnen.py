import geopandas as gpd

# Aus der WFS Datei verlinkt unter https://daten.berlin.de/datensaetze/trinkbrunnen_bwb?
url = "https://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer?service=WFS&version=2.0.0&request=GetFeature&typeNames=Trinkbrunnen_BWB:Trinkbrunnen_BWB&outputFormat=geojson"

gdf = gpd.read_file(url)
print(gdf.head())
gdf.to_csv("trinkbrunnen_berlin.csv", index=False)
