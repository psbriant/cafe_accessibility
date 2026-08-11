"""
Build an interactive Folium map showing King County Metro bus stops,
Seattle coffee shops, and Metro transit routes.
 
Input files:
  - kcm_bus_stops_cleaned.csv  (coordinates in WA State Plane North, EPSG:2285, feet)
  - coffee_shops.csv           (coordinates as WKT "POINT (lon lat)" in EPSG:4326)
  - Transit_Routes.shp (+ .shx/.dbf/.prj/.cpg)  (line geometries, WA State Plane North, feet)
 
Output:
  - coffee_and_bus_map.html
"""

import logging 
import re

import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from pyproj import Transformer

BUS_STOPS_CSV = "kcm_bus_stops_cleaned.csv"
COFFEE_SHOPS_CSV = "coffee_shops.csv"
TRANSIT_ROUTES_SHP = "Transit_Routes.shp"
OUTPUT_HTML = "coffee_and_bus_map.html"
 
# ---------------------------------------------------------------------------
# Load bus stops and reproject from WA State Plane North (feet) to lat/lon
# ---------------------------------------------------------------------------
bus_df = pd.read_csv(BUS_STOPS_CSV)
 
transformer = Transformer.from_crs("EPSG:2285", "EPSG:4326", always_xy=True)
lon, lat = transformer.transform(bus_df["XCOORD"].values, bus_df["YCOORD"].values)
bus_df["lat"] = lat
bus_df["lon"] = lon
 
# ---------------------------------------------------------------------------
# Load coffee shops and parse the WKT "POINT (lon lat)" geometry column
# ---------------------------------------------------------------------------
coffee_df = pd.read_csv(COFFEE_SHOPS_CSV)
 
 
def parse_point(wkt):
    wkt = str(wkt)
 
    # Simple point geometry: "POINT (lon lat)"
    match = re.match(r"POINT \(([-\d.]+) ([-\d.]+)\)", wkt)
    if match:
        return float(match.group(2)), float(match.group(1))  # lat, lon
 
    # Polygon geometry (e.g. a building footprint): use the centroid
    match = re.match(r"POLYGON \(\((.+)\)\)", wkt)
    if match:
        coord_pairs = match.group(1).split(",")
        lons, lats = [], []
        for pair in coord_pairs:
            x_str, y_str = pair.strip().split()
            lons.append(float(x_str))
            lats.append(float(y_str))
        return sum(lats) / len(lats), sum(lons) / len(lons)
 
    return None, None
 
 
 
coffee_df[["lat", "lon"]] = coffee_df["geometry"].apply(
    lambda g: pd.Series(parse_point(g))
)
coffee_df = coffee_df.dropna(subset=["lat", "lon"])
 
# ---------------------------------------------------------------------------
# Load transit routes shapefile and reproject to WGS84 lat/lon
# ---------------------------------------------------------------------------
routes_gdf = gpd.read_file(TRANSIT_ROUTES_SHP)
routes_gdf = routes_gdf.to_crs(epsg=4326)
 
# ---------------------------------------------------------------------------
# Build the map, centered on Seattle
# ---------------------------------------------------------------------------
center_lat = coffee_df["lat"].mean()
center_lon = coffee_df["lon"].mean()
 
m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="cartodbpositron")
 
# --- Bus stops layer (clustered, since there are ~2,700 of them) ---
bus_layer = folium.FeatureGroup(name=f"Bus Stops ({len(bus_df)})")
bus_cluster = MarkerCluster().add_to(bus_layer)
 
for _, row in bus_df.iterrows():
    popup_html = (
        f"<b>Stop ID:</b> {row['STOP_ID']}<br>"
        f"<b>Street:</b> {row['ON_STREET_NAME']}<br>"
        f"<b>Cross Street:</b> {row['HASTUS_CROSS_STREET_NAME']}<br>"
        f"<b>Routes:</b> {row['ROUTE_LIST']}"
    )
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=4,
        color="#1f77b4",
        fill=True,
        fill_color="#1f77b4",
        fill_opacity=0.8,
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=row["ON_STREET_NAME"],
    ).add_to(bus_cluster)
 
bus_layer.add_to(m)
 
# --- Coffee shops layer ---
coffee_layer = folium.FeatureGroup(name=f"Coffee Shops ({len(coffee_df)})")
 
for _, row in coffee_df.iterrows():
    address = f"{row.get('addr:housenumber', '')} {row.get('addr:street', '')}".strip()
    popup_html = (
        f"<b>{row['name']}</b><br>"
        f"{address}<br>"
        f"{row.get('addr:city', '')}, {row.get('addr:postcode', '')}"
    )
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=row["name"],
        icon=folium.Icon(color="darkred", icon="cutlery", prefix="fa"),
    ).add_to(coffee_layer)
 
coffee_layer.add_to(m)
 
# --- Transit routes layer ---
routes_layer = folium.FeatureGroup(name=f"Transit Routes ({len(routes_gdf)})")
 
folium.GeoJson(
    routes_gdf,
    style_function=lambda feature: {
        "color": "#2ca02c",
        "weight": 2.5,
        "opacity": 0.7,
    },
    highlight_function=lambda feature: {
        "color": "#ff7f0e",
        "weight": 4,
        "opacity": 1,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["ROUTE_NUM"],
        aliases=["Route:"],
    ),
    popup=folium.GeoJsonPopup(
        fields=["ROUTE_NUM", "ROUTE_ID", "LOCAL_EXPR", "CURRENT_NE"],
        aliases=["Route Number:", "Route ID:", "Type:", "Status:"],
        max_width=250,
    ),
).add_to(routes_layer)
 
routes_layer.add_to(m)
 
# Layer control to toggle each dataset on/off
folium.LayerControl(collapsed=False).add_to(m)
 
m.save(OUTPUT_HTML)
print(f"Map saved to {OUTPUT_HTML}")
print(f"Bus stops plotted: {len(bus_df)}")
print(f"Coffee shops plotted: {len(coffee_df)}")
print(f"Transit routes plotted: {len(routes_gdf)}")
