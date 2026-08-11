"""
Description: 
Pull geographic metadata for King County Metro bus stops for Seattle from the 
King County GIS Center.
"""

import logging
import os

import numpy as np
import pandas as pd


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(message)s',
                        level=logging.INFO)

    # ------------------------------------------------------------------------
    # ---INITIALIZE CONSTANT ARGUMENTS----------------------------------------
    # ------------------------------------------------------------------------
    
    main_path = "/Users/paul_briant/Documents/coding_projects/data/cafe_accessibility/"

    # ------------------------------------------------------------------------
    # ---GET DATA-------------------------------------------------------------
    # Read in bus stop location data from King County Metro
    # ------------------------------------------------------------------------
    
    bus_stops = pd.read_csv(f'{main_path}king_county_bus_stop_data.csv')

    bus_stops = bus_stops[['STOP_ID', 
                           'STOP_STATUS', 
                           'XCOORD', 
                           'YCOORD', 
                           'STOP_TYPE', 
                           'ON_STREET_NAME', 
                           'HASTUS_CROSS_STREET_NAME', 
                           'AUTH_NAME', 
                           'ZIPCODE', 
                           'ROUTE_LIST']]

    # ------------------------------------------------------------------------
    # ---PREP DATA------------------------------------------------------------
    # ------------------------------------------------------------------------
    
    # Clean up data:
    # 1). Remove stops that are Inactive (INA) Closed (CLO) or PLN
    bus_stops = bus_stops[bus_stops['STOP_STATUS'] == 'ACT']
    # 2). Remove stops that are not for Regular Service (REG)
    bus_stops = bus_stops[bus_stops['STOP_TYPE'] == 'REG']
    # 3). Filter for Seattle zipcodes
    bus_stops = bus_stops[
        (bus_stops["ZIPCODE"] >= 98101) & (bus_stops["ZIPCODE"] <= 98199)]

    # Filter for stop owners that are within Seattle city limits
    bus_stops = bus_stops[bus_stops["AUTH_NAME"].isin([
        'Seattle', 
        'Port of Seattle', 
        'Unknown',
        'University of Washington', 
        'State Dept. of Transportation',
        'Private Owner', 
        'Boeing Aircraft Corporation',
        'South Seattle Community College', 
        'Federal Government'])]

    # ------------------------------------------------------------------------
    # ---OUTPUT DATA----------------------------------------------------------
    # ------------------------------------------------------------------------

    output_file = f'{main_path}kcm_bus_stops_cleaned.csv'

    bus_stops = bus_stops.reset_index(drop=True)
    bus_stops.to_csv(output_file, index=False)
