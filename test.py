import math

class Converters:
    eWGS84 = 0
    eGRS80 = 1
    eCLARK80M = 2
    gICS = 0
    gITM = 1

    def __init__(self):
        self.DatumList = []
        self.GridList = []

        # WGS84 data
        self.DatumList.append(self.DATUM(
            6378137.0,
            6356752.3142,
            0.00335281066474748,
            0.006694380004260807,
            0.0818191909289062,
            0,
            0,
            0
        ))

        # GRS80 data
        self.DatumList.append(self.DATUM(
            6378137.0,
            6356752.3141,
            0.0033528106811823,
            0.00669438002290272,
            0.0818191910428276,
            -48,
            55,
            52
        ))

        # Clark 1880 Modified data
        self.DatumList.append(self.DATUM(
            6378300.789,
            6356566.4116309,
            0.003407549767264,
            0.006803488139112318,
            0.08248325975076590,
            -235,
            -85,
            264
        ))

        self.GridList.append(self.GRID(
            # ICS data
            0.6145667421719,
            0.55386447682762762,
            1.00000,
            170251.555,
            2385259.0
        ))

        # ITM data
        self.GridList.append(self.GRID(
            0.61443473225468920,
            0.55386965463774187,
            1.0000067,
            219529.584,
            2885516.9488
        ))

    def pi(self):
        return math.pi

    def sin2(self, x):
        return math.sin(x) * math.sin(x)

    def cos2(self, x):
        return math.cos(x) * math.cos(x)

    def tan2(self, x):
        return math.tan(x) * math.tan(x)

    def tan4(self, x):
        return self.tan2(x) * self.tan2(x)

    class DATUM:
        def __init__(self, a, b, f, esq, e, dx, dy, dz):
            self.a = a
            self.b = b
            self.f = f
            self.esq = esq
            self.e = e
            self.dX = dx
            self.dY = dy
            self.dZ = dz

    class GRID:
        def __init__(self, lon0, lat0, k0, false_e, false_n):
            self.lon0 = lon0
            self.lat0 = lat0
            self.k0 = k0
            self.false_e = false_e
            self.false_n = false_n

    def itm2wgs84(self, N, E):
        # 1. Local Grid (ITM) -> GRS80
        lat80, lon80 = self.Grid2LatLon(N, E, self.gITM, self.eGRS80)

        # 2. Molodensky GRS80->WGS84
        lat84, lon84 = self.Molodensky(lat80, lon80, self.eGRS80, self.eWGS84)

        # Final results
        lat = lat84 * 180 / self.pi()
        lon = lon84 * 180 / self.pi()
        return lat, lon

    def wgs842itm(self, lat, lon):
        latr = lat * self.pi() / 180
        lonr = lon * self.pi() / 180

        # 1. Molodensky WGS84 -> GRS80
        lat80, lon80 = self.Molodensky(latr, lonr, self.eWGS84, self.eGRS80)

        # 2. Lat/Lon (GRS80) -> Local Grid (ITM)
        N, E = self.LatLon2Grid(lat80, lon80, self.eGRS80, self.gITM)
        return N, E

    def ics2wgs84(self, N, E):
        # 1. Local Grid (ICS) -> Clark_1880_modified
        lat80, lon80 = self.Grid2LatLon(N, E, self.gICS, self.eCLARK80M)

        # 2. Molodensky Clark_1880_modified -> WGS84
        lat84, lon84 = self.Molodensky(lat80, lon80, self.eCLARK80M, self.eWGS84)

        # Final results
        lat = lat84 * 180 / self.pi()
        lon = lon84 * 180 / self.pi()
        return lat, lon

    def wgs842ics(self, lat, lon):
        latr = lat * self.pi() / 180

    # The rest of the methods would follow in a similar manner.
    def Molodensky(self, ilat, ilon, from_datum, to_datum):
        # Retrieve the datum parameters for the source and target datums
        from_datum_params = self.DatumList[from_datum]
        to_datum_params = self.DatumList[to_datum]

        # Compute the differences in datum parameters
        dX = from_datum_params.dX - to_datum_params.dX
        dY = from_datum_params.dY - to_datum_params.dY
        dZ = from_datum_params.dZ - to_datum_params.dZ

        # Compute the trigonometric functions of the latitude and longitude
        slat = math.sin(ilat)
        clat = math.cos(ilat)
        slon = math.sin(ilon)
        clon = math.cos(ilon)

        # Compute the squared sine of the latitude
        ssqlat = slat * slat

        # Compute some common terms
        e2 = from_datum_params.e * from_datum_params.e
        e4 = e2 * e2
        e6 = e4 * e2
        eg = from_datum_params.e * from_datum_params.a / from_datum_params.b
        eg2 = eg * eg

        # Compute some intermediate variables
        rn = from_datum_params.a / math.sqrt(1 - from_datum_params.esq * ssqlat)
        rm = from_datum_params.a * (1 - from_datum_params.esq) / math.pow((1 - from_datum_params.esq * ssqlat), 1.5)
        da = to_datum_params.a - from_datum_params.a
        df = to_datum_params.f - from_datum_params.f

        # Compute the change in latitude (dlat)
        dlat = (-dX * slat * clon - dY * slat * slon + dZ * clat + da * rn * from_datum_params.esq * slat * clat / from_datum_params.a + df * (rm * (1.0 / (1 - from_datum_params.esq)) + rn / (1.0 / (1 - from_datum_params.esq))) * slat * clat) / (rm + 0.0)

        # Compute the new latitude
        olat = ilat + dlat

        # Compute the change in longitude (dlon)
        dlon = (-dX * slon + dY * clon) / ((rn + 0.0) * clat)

        # Compute the new longitude
        olon = ilon + dlon

        return olat, olon

    def LatLon2Grid(self, lat, lon, from_datum, to_grid):
        # Retrieve the datum parameters for the source datum
        from_datum_params = self.DatumList[from_datum]

        # Compute some common terms
        slat = math.sin(lat)
        clat = math.cos(lat)
        slon = math.sin(lon)
        clon = math.cos(lon)
        ssqlat = slat * slat
        e2 = from_datum_params.e * from_datum_params.e
        adb = 1.0 / (1.0 - from_datum_params.f)
        rn = from_datum_params.a / math.sqrt(1 - from_datum_params.esq * ssqlat)
        rm = from_datum_params.a * (1 - from_datum_params.esq) / math.pow((1 - from_datum_params.esq * ssqlat), 1.5)

        # Compute the easting (E) and northing (N) values
        K1 = rn * from_datum_params.k0
        K2 = (rn * from_datum_params.k0 * slat * clat / 2)
        K3 = (rn * from_datum_params.k0 * slat * clat * clat * clat * (5 - slat * slat + 9 * from_datum_params.e * from_datum_params.e * clat * clat)) / 24.0
        K4 = rn * from_datum_params.k0 * clat
        K5 = (rn * from_datum_params.k0 * clat * clat * clat * (1 - slat * slat + from_datum_params.e * from_datum_params.e * clat * clat)) / 6.0

        E = K1 * (lon - from_datum_params.lon0) + K2 * (lon - from_datum_params.lon0) * (lon - from_datum_params.lon0) + K3 * (lon - from_datum_params.lon0) * (lon - from_datum_params.lon0) * (lon - from_datum_params.lon0) * (lon - from_datum_params.lon0)
        N = K4 * (lat - from_datum_params.lat0) + K5 * (lat - from_datum_params.lat0) * (lat - from_datum_params.lat0) * (lat - from_datum_params.lat0)

        E += from_datum_params.false_e
        N += from_datum_params.false_n

        # Apply grid scale factor
        E *= to_grid.k0
        N *= to_grid.k0

        return E, N


# Example usage
converter = Converters()
N, E = converter.wgs842itm(31.776687, 35.234203)
print("ITM Coordinates: N =", N, "E =", E)
