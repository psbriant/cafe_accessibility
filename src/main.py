"""
Description: 

Build an interactive Folium map showing King County Metro bus stops,
Seattle coffee shops, and Metro transit routes.
 
Input datasets:

1). King county metro bus stops for Seattle (coordinates in WA State Plane
    North, EPSG:2285, feet)
2). Seattle coffee shops and their walking isochrones (isochrome_cafe_data.
    json, geocoded coordinates and isochrone polygons from the Mapbox
    Isochrone API, EPSG:4326)
3). King County Metro bus routes, (.shx/.dbf/.prj/.cpg, line geometries, WA
    State Plane North, feet)
 
Outputs:

1). coffee_and_bus_map.html
"""

import json
import logging

import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
from pyproj import Transformer

import constants as cts


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO)

    # ------------------------------------------------------------------------
    # ---LOAD DATA------------------------------------------------------------
    # ------------------------------------------------------------------------

    # Load bus stops and reproject from WA State Plane North (feet) to lat/lon
    logging.info("Loading bus stop data")
    bus_df = pd.read_csv(cts.BUS_STOPS_CLEANED_CSV)
    
    transformer = Transformer.from_crs(
        "EPSG:2285", 
        "EPSG:4326", 
        always_xy=True)
    
    lon, lat = transformer.transform(
        bus_df["XCOORD"].values, 
        bus_df["YCOORD"].values)
    
    bus_df["lat"] = lat
    bus_df["lon"] = lon
 
    # Load coffee shops and their walking isochrones
    logging.info("Loading coffee shop and isochrone data")
    with open(cts.ISOCHROME_DATA) as f:
        isochrone_data = json.load(f)

    coffee_df = pd.DataFrame([
        {
            "name": name,
            "addr:city": entry["address_metadata"].get("addr_city", ""),
            "addr:postcode": entry["address_metadata"].get("addr_postcode", ""),
            "lat": entry["address_metadata"]["lat"],
            "lon": entry["address_metadata"]["lon"],
        }
        for name, entry in isochrone_data.items()
    ])

    # Load transit routes shapefile and reproject to WGS84 lat/lon
    logging.info("Loading King County Metro bus routes from shapefile")
    routes_gdf = gpd.read_file(cts.TRANSIT_ROUTES_SHP)
    routes_gdf = routes_gdf.to_crs(epsg=4326)
 
    # ------------------------------------------------------------------------
    # ---BUILD THE MAP--------------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Building the map")

    # Center the map on Seattle
    center_lat = coffee_df["lat"].mean()
    center_lon = coffee_df["lon"].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=12, 
        tiles="cartodbpositron")
    
    # ------------------------------------------------------------------------
    # ---ADD BUS STOPS--------------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Creating bus stop layer")

    # Bus stops layer (clustered, since there are ~2,700 of them)
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
    
    # ------------------------------------------------------------------------
    # ---ADD COFFEE SHOPS-----------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Creating coffee shop layer")

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
    
    # ------------------------------------------------------------------------
    # ---ADD TRANSIT ROUTES---------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Creating transit routes layer")

    routes_layer = folium.FeatureGroup(
        name=f"Transit Routes ({len(routes_gdf)})")
    
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

    # ------------------------------------------------------------------------
    # ---ADD LAYER CONTROL----------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Adding layer control")

    # Layer control to toggle each dataset on/off
    folium.LayerControl(collapsed=False).add_to(m)

    # ------------------------------------------------------------------------
    # ---OUTPUT MAP-----------------------------------------------------------
    # ------------------------------------------------------------------------
    
    logging.info("Outputting map")
    
    m.save(cts.OUTPUT_HTML)
    logging.info(f"Map saved to {cts.OUTPUT_HTML}")
    logging.info(f"Bus stops plotted: {len(bus_df)}")
    logging.info(f"Coffee shops plotted: {len(coffee_df)}")
    logging.info(f"Transit routes plotted: {len(routes_gdf)}")
