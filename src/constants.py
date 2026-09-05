"""
Description: 

File for storing recurring settings.
"""

from dotenv import load_dotenv
import os

# Load mapbox api token
load_dotenv() 
TOKEN = os.environ["MAPBOX_TOKEN"]

# Set time interval
INTERVAL = 5

# List of Seattle zipcodes
SEATTLE_ZIPCODES = [98101, 98102, 98103, 98104, 98105, 98106, 98107, 98108, 
                    98109, 98112, 98115, 98116, 98117, 98118, 98119, 98121, 
                    98122, 98125, 98126, 98133, 98134, 98136, 98144, 98146,
                    98174, 98177, 98178, 98195, 98199]

# Main file path for inputs and outputs
MAIN_PATH = "/Users/paul_briant/Documents/coding_projects/data/cafe_accessibility/"

# Paths for output files
BUS_STOPS_RAW_CSV = f"{MAIN_PATH}king_county_bus_stop_data.csv"
BUS_STOPS_CLEANED_CSV = f"{MAIN_PATH}kcm_bus_stops_cleaned.csv"
COFFEE_SHOPS_CSV = f"{MAIN_PATH}coffee_shops.csv"
TRANSIT_ROUTES_SHP = f"{MAIN_PATH}Transit_Routes.shp"
OUTPUT_HTML = f"{MAIN_PATH}coffee_and_bus_map.html"
ISOCHROME_DATA = f"{MAIN_PATH}isochrome_cafe_data.json"
