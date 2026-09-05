"""
Description:

Pull isochrone data from mapbox and add coffee shop data to an output json 
file.
"""

import json
import logging

import pandas as pd
import requests

from coordinate_utils import parse_point
import constants as cts

logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO)


if __name__ == "__main__":

    # Load coffee shops and parse the WKT "POINT (lon lat)" geometry column
    logging.info("Loading coffee shop data")
    coffee_df = pd.read_csv(cts.COFFEE_SHOPS_CSV)
    
    coffee_df[["lat", "lon"]] = coffee_df["geometry"].apply(
            lambda g: pd.Series(parse_point(g))
        )
    coffee_df = coffee_df.dropna(subset=["lat", "lon"])

    # Cafe coordinate data: 

    # ------------------------------------------------------------------------
    # ---PULL DATA------------------------------------------------------------
    # ------------------------------------------------------------------------
    
    coffee_merged = {}

    for _, row in coffee_df.iterrows():

        name = row['name']

        logging.info(f"Parsing address metadata for {name}")
        
        address = f"{row.get('addr:housenumber', '')} {row.get('addr:street', '')}".strip()
        addr_city = row.get('addr:city', '')
        addr_city = None if pd.isna(addr_city) else addr_city
        addr_postcode = row.get('addr:postcode', '')
        addr_postcode = None if pd.isna(addr_postcode) else addr_postcode
        lon = row['lon']
        lat = row['lat']

        # Construct the URL of the isochrone request.
        url = f"https://api.mapbox.com/isochrone/v1/mapbox/walking/{lon},{lat}?contours_minutes={cts.INTERVAL}&polygons=true&access_token={cts.TOKEN}"

        # Performs HTTP request and gets the response data.
        logging.info("Making request to API for isochrome data")

        try:
            response = requests.get(url)
            data = response.json()

        except:
            raise ValueError(
                "There is an issue with the api request for the coffee shop {name}")

        # Add address metadata to json
        logging.info("Adding address metadata to json")
        data['address_metadata'] = {
            'addr_city': addr_city, 
            'addr_postcode': addr_postcode, 
            'lon': lon,
            'lat': lat}

        coffee_merged[name] = data

    # ------------------------------------------------------------------------
    # ---WRITING JSON TO DISK-------------------------------------------------
    # ------------------------------------------------------------------------

    logging.info("Outputting json")
    with open(cts.ISOCHROME_DATA, "w") as f:
        json.dump(coffee_merged, f, allow_nan=False)
