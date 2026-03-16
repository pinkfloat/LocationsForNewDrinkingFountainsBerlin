import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# ==============================
# GENERAL SETTINGS
# ==============================
TARGET_CRS = "EPSG:4326"
pd.set_option('display.max_columns', None)

# ==============================
# LOAD & CLEAN DATASETS
# ==============================
def load_points_csv(path):
    df = pd.read_csv(path)
    df = df[df["name"].notna()].copy()
    df["geometry"] = df["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    return gdf.to_crs(TARGET_CRS)

stops = load_points_csv("Haltestellen/oepnv_02_osmnx_result.csv")
stores = load_points_csv("Getraenke_Laeden/stores_02_osmnx_result.csv")

def load_geojson_fix_crs(path):
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs("EPSG:4326", allow_override=True)
    return gdf.to_crs(TARGET_CRS)

fountains = load_geojson_fix_crs("Trinkbrunnen/trinkwasserbrunnen_trinkwasserbrunnen_WGS84.geojson")
berlin_area = load_geojson_fix_crs("Flaechennutzung/berlin_area_merged.geojson")
new_fountains = load_geojson_fix_crs("new_calculated_fountains.geojson")

# -------------------------------------------------
# Map center (Berlin)
# -------------------------------------------------
m = folium.Map(location=[52.52, 13.405], zoom_start=12, tiles="CartoDB positron")

# -------------------------------------------------
# Feature Groups (Layers)
# -------------------------------------------------
fountains_fg = folium.FeatureGroup(name="Drinking Fountains")
new_fountains_fg = folium.FeatureGroup(name="New Fountains")
stops_fg = folium.FeatureGroup(name="Public Transport Stops")
stores_fg = folium.FeatureGroup(name="Beverage Stores")
berlin_area_fg = folium.FeatureGroup(name="Berlin Areas")

# Coarse areas, so the website doesn't get too slow
berlin_area["geometry"] = berlin_area["geometry"].simplify(
    tolerance=0.0001,
    preserve_topology=True
)

# -------------------------------------------------
# MarkerCluster for large datasets
# -------------------------------------------------
stops_cluster = MarkerCluster().add_to(stops_fg)
stores_cluster = MarkerCluster().add_to(stores_fg)

# -------------------------------------------------
# Drinking fountains (blue markers)
# -------------------------------------------------
for _, row in fountains.iterrows():
    fountain_id = row.get('nummer', 'N/A')

    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4,
        color="blue",
        fill=True,
        fill_opacity=0.8,
        popup=f"Drinking Fountain No: {fountain_id}"
    ).add_to(fountains_fg)

# -------------------------------------------------
# New calc. Drinking fountains (purple markers)
# -------------------------------------------------
for _, row in new_fountains.iterrows():
    fountain_id = row.get('nummer')

    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=4,
        color="purple",
        fill=True,
        fill_opacity=0.8,
        popup=f"New Fountain No: {fountain_id}"
    ).add_to(new_fountains_fg)

# -------------------------------------------------
# Public transport stops (yellow, clustered)
# -------------------------------------------------
for _, row in stops.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="yellow",
        fill=True,
        fill_opacity=0.6,
        popup=row.get("name", "Stop")
    ).add_to(stops_cluster)

# -------------------------------------------------
# Beverage stores (red, clustered)
# -------------------------------------------------
for _, row in stores.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=row.get("name", "Store")
    ).add_to(stores_cluster)

# -------------------------------------------------
# Berlin Areas (polygon layer)
# -------------------------------------------------

# Color mapping based on "nutz" columns
nutz_colors = {
    "10":  "#f4cccc",  # Residential use (light red / soft pink)
    "21":  "#f6b26b",  # Mixed use (light orange)
    "30":  "#e69138",  # Core urban area (medium orange)
    "40":  "#999999",  # Commercial and industrial use, large-scale retail (medium gray)
    "50":  "#c27ba0",  # Public services and special use (muted purple)
    "60":  "#8e7cc3",  # Utilities and supply infrastructure (medium violet)
    "70":  "#b6d7a8",  # Weekend housing / garden-like residential use (pale green)

    "80":  "#bdbdbd",  # Traffic area (excluding roads) (light gray)
    "90":  "#d9d9d9",  # Construction site (very light gray)

    "100": "#006400",  # Forest (dark green)

    "110": "#1f78ff",  # Water body (bright blue)

    "121": "#98fb98",  # Grassland (pale green)
    "122": "#b7e1a1",  # Arable land (soft yellow-green)

    "130": "#a8e6a3",  # Park / Green space (light fresh green)
    "140": "#d0e0e3",  # City square / promenade (light bluish gray)

    "150": "#c5e8b7",  # Cemetery (muted light green)
    "160": "#b4f0b4",  # Allotment garden (bright light green)

    "171": "#e2f0d9",  # Brownfield, vegetation-free (very pale green)
    "172": "#cfe8cf",  # Brownfield with meadow-like vegetation (soft desaturated green)
    "173": "#b7d7b7",  # Brownfield with mixed vegetation (medium desaturated green)

    "190": "#6fa8dc",  # Sports area (soft blue)

    "200": "#93c47d",  # Tree nursery / horticulture (natural medium green)
}
default_color = "#dddddd"  # Default fallback color (neutral light gray)

def style_function(feature):
    nutz_value = str(feature["properties"]["nutz"])
    return {
        "fillColor": nutz_colors.get(nutz_value, default_color),
        "color": "black",
        "weight": 0.3,
        "fillOpacity": 0.5,
    }

folium.GeoJson(
    berlin_area,
    name="Berlin Areas",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["bezirk", "enutzung", "ew2023"],
        aliases=["District:", "Usage:", "Residents 2023:"]
    )
).add_to(berlin_area_fg)

# -------------------------------------------------
# Add layers to map
# -------------------------------------------------
# Note: The order matters in terms of "clicking on items"
# So having the areas first makes everthing "over them"
# better clickable.
berlin_area_fg.add_to(m)
stops_fg.add_to(m)
stores_fg.add_to(m)
fountains_fg.add_to(m)
new_fountains_fg.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

file_path = "berlin_drinking_fountain_analysis.html"
m.save(file_path)

webbrowser.open('file://' + os.path.realpath(file_path))
