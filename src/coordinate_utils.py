"""
Description: 

Utilty fuctions for managing coordinate systems. 
"""

import re


def parse_point(wkt: str) -> tuple:
    """
    Parses open street maps geographic coordinate data so that it can be used 
    with King county metro bus stop and bus route geographic data which both 
    use the Washington State Plane North. 

    The open streetmap data is in both point data and polygon data. This 
    function converts the polygon data into point data. 

    Arguments:
        wkt (str): Coordinates in the Well Known Text (WKT) formate. More 
            information at https://www.ogc.org/standards/wkt-crs/

    Returns:
        Returns a tuple of coordinate pairs (lat and long):

            1). If point geometry: returns the lat and long
            2). If polygon geometry: returns the average of the polygon lat 
                and longs.
            3). If neither: returns none for both lat and long.
       
    Raises:
        None
    """

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
