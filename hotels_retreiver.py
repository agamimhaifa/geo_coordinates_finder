import overpy
import csv
import requests


def get_hotels_csv(filename):
    csv_hotels = []
    # Open and read the CSV file
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)

        # Skip the header row (first row)
        next(csv_reader)
        # Iterate through each row in the CSV
        for row in csv_reader:
            # Each row is a list of values values are accessed via specific columns using indexing (e.g., row[0], row[1])
            print('processing :' , row)
            csv_hotels.append(row)

    
    responses = list()
    # Iterate through each row in the CSV
    for row in csv_hotels:
        # Each row is a list of values
        # You can access specific columns using indexing (e.g., row[0], row[1])
        print('processing :' , row)
        hotel_city, addr_name = row
        # Make the API request to Nominatim
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": addr_name + ' ' + hotel_city,
            "format": "json"
        }

        response = requests.get(base_url, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                # Create a copy of the response object
                responses.append(data)
        else:
            print(f"Original request failed with status code {response.status_code}")

    hotels = []
    for resp in responses:  
        # Extract the latitude and longitude from the first result
        name = resp[0]['name']
        display_name = resp[0]['display_name']
        geolatitude = resp[0]['lat']
        geolongitude = resp[0]['lon']
        print(f'Latitude: {geolatitude}, Longitude: {geolongitude}')

        hotel = dict()
        hotel["Name"] = name
        hotel["Latitude"] = geolongitude
        hotel["Longitude"] = geolatitude 
        hotels.append(hotel)

    return hotels


def get_hotels_osm(lat1, lon1, lat2, lon2):
    hotels = {}
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
    entries = result.nodes + result.ways + result.relations
    for ent in entries:
        print(ent)
        hotels["Name"] = ent.tags.get('name', 'N/A')
        hotels["Latitude"] = ent.lat 
        hotels["Longitude"] = ent.lon 

    return hotels

if __name__ == "__main__":
    hotels = get_hotels_csv(filename='hotels.csv')
    for h in hotels:
        print(h)

    lat1 = 32.83268436193918
    lon1 = 34.955532887683354
    lat2 = 35.06311516001032
    lon2 = 32.75769371634262

    hotels = get_hotels_osm(lat1, lon1, lat2, lon2)
    for h in hotels:
        print(h)