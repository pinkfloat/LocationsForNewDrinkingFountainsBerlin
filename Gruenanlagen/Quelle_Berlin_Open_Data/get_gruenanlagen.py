import geopandas as gpd

url = "https://gdi.berlin.de/services/wfs/gruenanlagen?service=WFS&version=2.0.0&request=GetFeature&typeNames=gruenanlagen:gruenanlagen&outputFormat=application/json"

gdf = gpd.read_file(url)
print(gdf.head())
gdf.to_csv("gruenanlagen_berlin.csv", index=False)
