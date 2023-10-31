import overpy

def get_hotels_in_bbox(lat1, lon1, lat2, lon2):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    (
      node["tourism"="hotel"]({lat1},{lon1},{lat2},{lon2});
      way["tourism"="hotel"]({lat1},{lon1},{lat2},{lon2});
      relation["tourism"="hotel"]({lat1},{lon1},{lat2},{lon2});
    );
    out center;
    """
    result = api.query(query)
    return result.nodes + result.ways + result.relations

