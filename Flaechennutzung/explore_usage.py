import geopandas as gpd

filename = "ua_flaechennutzung_c_reale_nutzung_2022_WGS84.geojson"

gdf = gpd.read_file(filename)

# nutz → nutzung
nutz_df = (
    gdf[["nutz", "nutzung"]]
    .drop_duplicates()
    .sort_values("nutz")
)

print("\n=== 'nutz' → 'nutzung' ===")
print(nutz_df.to_string(index=False))

# typ → typklar
typ_df = (
    gdf[["typ", "typ_klar"]]
    .drop_duplicates()
    .sort_values("typ")
)

print("\n=== 'typ' → 'typ_klar' ===")
print(typ_df.to_string(index=False)) 
