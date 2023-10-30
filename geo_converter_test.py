from geo_converter import Converters 


def test_conversions1():
    converters = Converters()

    # Test ITM to WGS84 conversion
    N, E = 178899, 663970
    #lat, lon = converters.itm2wgs84(N, E)
    print(f"ITM to WGS84: Lat: {lat}, Lon: {lon}")

    # Test WGS84 to ITM conversion
    lat, lon = 32.086139, 34.780126  # Example WGS84 coordinates
    N, E = converters.wgs842itm(lat, lon)
    print(f"WGS84 to ITM: N: {N}, E: {E}")

    # Test ICS to WGS84 conversion
    N, E = 208148, 648456
    lat, lon = converters.ics2wgs84(N, E)
    print(f"ICS to WGS84: Lat: {lat}, Lon: {lon}")

    # Test WGS84 to ICS conversion
    lat, lon = 31.891623, 34.768842  # Example WGS84 coordinates
    N, E = converters.wgs842ics(lat, lon)
    print(f"WGS84 to ICS: N: {N}, E: {E}")


def test_conversions2():
    converters = Converters()
    # Example usage
    N = 174130
    E = 661949
    itm_lat, itm_lon = converters.itm2wgs84(N, E)
    print(f"ITM to WGS84: Latitude: {itm_lat}, Longitude: {itm_lon}")

    wgs84_lat = 32.085299
    wgs84_lon = 34.781767
    N, E = converters.wgs842itm(wgs84_lat, wgs84_lon)
    print(f"WGS84 to ITM: North: {N}, East: {E}")

if __name__ == "__main__":
    test_conversions1()
    test_conversions2()