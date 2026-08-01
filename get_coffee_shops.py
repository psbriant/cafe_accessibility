"""
Description: 
Pull location data from open street maps for coffee shops in Seattle. 
"""

import numpy as np
import osmnx as ox
import pandas as pd


if __name__ == "__main__":

    # ------------------------------------------------------------------------
    # ---INITIALIZE CONSTANT ARGUMENTS----------------------------------------
    # ------------------------------------------------------------------------
    
    # Global path variables
    main_path = "/Users/paul_briant/Documents/coding_projects/data/cafe_accessibility/"

    # ------------------------------------------------------------------------
    # ---PULL DATA------------------------------------------------------------
    # ------------------------------------------------------------------------

    # Pull location data for Seattle coffeeshops from Open Street Maps
    place = "Seattle, United States"
    aoi = ox.geocoder.geocode_to_gdf(place)
    tags = {"cuisine": True}
    businesses = ox.features.features_from_place(place, tags)

    # ------------------------------------------------------------------------
    # ---PREP DATA------------------------------------------------------------
    # ------------------------------------------------------------------------

    # Subset data to necessary columns only and coffee shops
    coffee_shops = businesses.copy()
    coffee_shops = coffee_shops[['name', 
                                 'cuisine', 
                                 'addr:housenumber', 
                                 'addr:street', 
                                 'addr:city', 
                                 'addr:postcode', 
                                 'geometry']]
    coffee_shops = coffee_shops[coffee_shops['cuisine'] == 'coffee_shop']

    # ------------------------------------------------------------------------
    # ---OUTPUT DATA----------------------------------------------------------
    # ------------------------------------------------------------------------

    output_file = f'{main_path}coffee_shops.csv'

    coffee_shops.to_csv(output_file)
