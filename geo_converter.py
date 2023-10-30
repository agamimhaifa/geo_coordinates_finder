#*****************************************************************************************************
#*                                                                                                   *
#*  This code is free software; you can redistribute it and/or modify it at your will.               *
#*  It is our hope however that if you improve it in any way you will find a way to share it too.     *
#*                                                                                                   *
#*  Original C++ version by jgray77@gmail.com	3/2010								                  *
#*  Ported C# version by mikisiton2@gmail.com	5/2012								                  *
#*                                                                                                   *
#*  This program is distributed AS-IS in the hope that it will be useful, but WITHOUT ANY WARRANTY;  *
#*  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.        * 
#*                                                                                                   *
#*****************************************************************************************************
#
#
#===================================================================================================
#	Israel Local Grids <==> WGS84 conversions
#===================================================================================================
#
# The Israel New Grid (ITM) is a Transverse Mercator projection of the GRS80 ellipsoid.
# The Israel Old Grid (ICS) is a Cassini-Soldner projection of the modified Clark 1880 ellipsoid.
#
# To convert from a local grid to WGS84 you first do a "UTM to Lat/Lon" conversion using the 
# known formulas but with the local grid data (Central Meridian, Scale Factor and False 
# Easting and Northing). This results in Lat/Long in the local ellipsoid coordinate system.
# Afterwards you do a Molodensky transformation from this ellipsoid to WGS84.
#
# To convert from WGS84 to a local grid you first do a Molodensky transformation from WGS84
# to the local ellipsoid, after which you do a Lat/Lon to UTM conversion, again with the data of
# the local grid instead of the UTM data.
#
# The UTM to Lat/Lon and Lat/Lon to UTM conversion formulas were taken as-is from the
# excellent article by Prof.Steven Dutch of the University of Wisconsin at Green Bay:
#		http:#www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm
#
# The [abridged] Molodensky transformations were taken from
#		http:#home.hiwaay.net/~taylorc/bookshelf/math-science/geodesy/datum/transform/molodensky/
# and can be found in many sources on the net.
# 
# Additional sources:
# ===================
# 1. dX,dY,dZ values:  http:#www.geo.hunter.cuny.edu/gis/docs/geographic_transformations.pdf
#
# 2. ITM data:  http:#www.mapi.gov.il/geodesy/itm_ftp.txt
#    for the meridional arc false northing, the value is given at
#    http:#www.mapi.gov.il/reg_inst/dir2b.doc	
#    (this doc also gives a different formula for Lat/lon -> ITM, but not the reverse)
#
# 3. ICS data:  http:#www.mapi.gov.il/geodesy/ics_ftp.txt
#    for the meridional arc false northing, the value is given at several places as the 
#    correction value for Garmin GPS sets, the origin is unknown.
#    e.g. http:#www.idobartana.com/etrexkb/etrexisr.htm
#	
# Notes: 
# ======
# 1. The conversions between ICS and ITM are 
#			ITM Lat = ICS Lat - 500000
#			ITM Lon = ICS Lon + 50000
#	  e.g. ITM 678000,230000 <--> ICS 1178000 180000
#
#	  Since the formulas for ITM->WGS84 and ICS->WGS84 are different, the results will differ.
#    For the above coordinates we get the following results (WGS84)
#		ITM->WGS84 32.11'43.945" 35.18'58.782"
#		ICS->WGS84 32.11'43.873" 35.18'58.200"
#      Difference    ~3m            ~15m
#
# 2. If you have, or have seen, formulas that contain the term Sin(1"), I recommend you read 
#    Prof.Dutch's enlightening explanation about it in his link above.
#
#===================================================================================================


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
            0.6145667421719,
            0.55386447682762762,
            1.00000,
            170251.555,
            2385259.0
        ))

        self.GridList.append(self.GRID(
            0.61443473225468920,
            0.55386965463774187,
            1.0000067,
            219529.584,
            2885516.9488
        ))

    def pi(self):
        return 3.141592653589793

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
            self.false_n = false_n
            self.false_e = false_e


    #=================================================
    # Israel New Grid (ITM) to WGS84 conversion
    #=================================================
    def itm2wgs84(self, N, E):
        lat80, lon80 = self.grid2latlon(N, E, self.gITM, self.eGRS80)
        lat84, lon84 = self.molodensky(lat80, lon80, self.eGRS80, self.eWGS84)
        lat = lat84 * 180 / self.pi()
        lon = lon84 * 180 / self.pi()
        return lat, lon

    #=================================================
    # WGS84 to Israel New Grid (ITM) conversion
    #=================================================
    def wgs842itm(self, lat, lon):
        latr = lat * self.pi() / 180
        lonr = lon * self.pi() / 180
        lat80, lon80 = self.molodensky(latr, lonr, self.eWGS84, self.eGRS80)
        N, E = self.latlon2grid(lat80, lon80, self.eGRS80, self.gITM)
        return N, E

    #=================================================
    # Israel Old Grid (ICS) to WGS84 conversion
    #=================================================
    def ics2wgs84(self, N, E):
        lat80, lon80 = self.grid2latlon(N, E, self.gICS, self.eCLARK80M)
        lat84, lon84 = self.molodensky(lat80, lon80, self.eCLARK80M, self.eWGS84)
        lat = lat84 * 180 / self.pi()
        lon = lon84 * 180 / self.pi()
        return lat, lon

    #=================================================
    # WGS84 to Israel Old Grid (ICS) conversion
    #=================================================
    def wgs842ics(self, lat, lon):
        latr = lat * self.pi() / 180
        lonr = lon * self.pi() / 180
        lat80, lon80 = self.molodensky(latr, lonr, self.eWGS84, self.eCLARK80M)
        N, E = self.latlon2grid(lat80, lon80, self.eCLARK80M, self.gICS)
        return N, E

    #====================================
    # Local Grid to Lat/Lon conversion
    #====================================
    def grid2latlon(self, N, E, from_datum, to_datum):
        y = N + self.GridList[from_datum].false_n
        x = E - self.GridList[from_datum].false_e
        M = y / self.GridList[from_datum].k0
        a = self.DatumList[to_datum].a
        b = self.DatumList[to_datum].b
        e = self.DatumList[to_datum].e
        esq = self.DatumList[to_datum].esq
        mu = M / (a * (1 - e * e / 4 - 3 * e * e * e * e / 64 - 5 * e * e * e * e * e * e / 256))
        ee = math.sqrt(1 - esq)
        e1 = (1 - ee) / (1 + ee)
        j1 = 3 * e1 / 2 - 27 * e1 * e1 * e1 / 32
        j2 = 21 * e1 * e1 / 16 - 55 * e1 * e1 * e1 * e1 / 32
        j3 = 151 * e1 * e1 * e1 / 96
        j4 = 1097 * e1 * e1 * e1 * e1 / 512
        fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)
        sinfp = math.sin(fp)
        cosfp = math.cos(fp)
        tanfp = sinfp / cosfp
        eg = (e * a / b)
        eg2 = eg * eg
        C1 = eg2 * cosfp * cosfp
        T1 = tanfp * tanfp
        R1 = a * (1 - e * e) / math.pow(1 - (e * sinfp) * (e * sinfp), 1.5)
        N1 = a / math.sqrt(1 - (e * sinfp) * (e * sinfp))
        D = x / (N1 * self.GridList[from_datum].k0)
        Q1 = N1 * tanfp / R1
        Q2 = D * D / 2
        Q3 = (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * eg2 * eg2) * (D * D * D * D) / 24
        Q4 = (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 3 * C1 * C1 - 252 * eg2 * eg2) * (D * D * D * D * D * D) / 720
        lat = fp - Q1 * (Q2 - Q3 + Q4)
        Q5 = D
        Q6 = (1 + 2 * T1 + C1) * (D * D * D) / 6
        Q7 = (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * eg2 * eg2 + 24 * T1 * T1) * (D * D * D * D * D) / 120
        lon = self.GridList[from_datum].lon0 + (Q5 - Q6 + Q7) / cosfp
        return lat, lon

    #====================================
    # Lat/Lon to Local Grid conversion
    #====================================
    def latlon2grid(self, lat, lon, from_datum, to_datum):
        a = self.DatumList[from_datum].a
        e = self.DatumList[from_datum].e
        b = self.DatumList[from_datum].b
        slat1 = math.sin(lat)
        clat1 = math.cos(lat)
        clat1sq = clat1 * clat1
        tanlat1sq = slat1 * slat1 / clat1sq
        e2 = e * e
        e4 = e2 * e2
        e6 = e4 * e2
        eg = (e * a / b)
        eg2 = eg * eg
        l1 = 1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256
        l2 = 3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024
        l3 = 15 * e4 / 256 + 45 * e6 / 1024
        l4 = 35 * e6 / 3072
        M = a * (l1 * lat - l2 * math.sin(2 * lat) + l3 * math.sin(4 * lat) - l4 * math.sin(6 * lat))
        nu = a / math.sqrt(1 - (e * slat1) * (e * slat1))
        p = lon - self.GridList[to_datum].lon0
        k0 = self.GridList[to_datum].k0
        K1 = M * k0
        K2 = k0 * nu * slat1 * clat1 / 2
        K3 = (k0 * nu * slat1 * clat1 * clat1sq / 24) * (5 - tanlat1sq + 9 * eg2 * clat1sq + 4 * eg2 * eg2 * clat1sq * clat1sq)
        Y = K1 + K2 * p * p + K3 * p * p * p * p - self.GridList[to_datum].false_n
        K4 = k0 * nu * clat1
        K5 = (k0 * nu * clat1 * clat1sq / 6) * (1 - tanlat1sq + eg2 * clat1 * clat1)
        X = K4 * p + K5 * p * p * p + self.GridList[to_datum].false_e
        E = int(X + 0.5)
        N = int(Y + 0.5)
        return N, E

    #======================================================
    # Abridged Molodensky transformation between 2 datums
    #======================================================
    def molodensky(self, ilat, ilon, from_datum, to_datum):
        dX = self.DatumList[from_datum].dX - self.DatumList[to_datum].dX
        dY = self.DatumList[from_datum].dY - self.DatumList[to_datum].dY
        dZ = self.DatumList[from_datum].dZ - self.DatumList[to_datum].dZ
        slat = math.sin(ilat)
        clat = math.cos(ilat)
        slon = math.sin(ilon)
        clon = math.cos(ilon)
        ssqlat = slat * slat
        from_f = self.DatumList[from_datum].f
        df = self.DatumList[to_datum].f - from_f
        from_a = self.DatumList[from_datum].a
        da = self.DatumList[to_datum].a - from_a
        from_esq = self.DatumList[from_datum].esq
        adb = 1.0 / (1.0 - from_f)
        rn = from_a / math.sqrt(1 - from_esq * ssqlat)
        rm = from_a * (1 - from_esq) / math.pow((1 - from_esq * ssqlat), 1.5)
        from_h = 0.0
        dlat = (-dX * slat * clon - dY * slat * slon + dZ * clat + da * rn * from_esq * slat * clat / from_a +
                df * (rm * adb + rn / adb) * slat * clat) / (rm + from_h)
        olat = ilat + dlat
        dlon = (-dX * slon + dY * clon) / ((rn + from_h) * clat)
        olon = ilon + dlon
        return olat, olon


