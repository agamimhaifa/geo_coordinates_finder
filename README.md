# Various geo locations finder  

Given a name of some place that can be searched in google maps or openstreetmap 
The app will search the name using openstreetmap REST api.
The app will return 
- Israel Local Grids (ITM) via WGS84 conversions [WGS84 - World Geodetic System](https://en.wikipedia.org/wiki/World_Geodetic_System)

The Israel New Grid (ITM) is a Transverse Mercator projection of the GRS80 ellipsoid.
The Israel Old Grid (ICS) is a Cassini-Soldner projection of the modified Clark 1880 ellipsoid.

openstreetmap returns WGS84 Lat/Long coordinates which are converted to ITM

To convert from WGS84 to a local grid you first do a Molodensky transformation from WGS84
to the local ellipsoid, after which you do a Lat/Lon to UTM conversion, again with the data of
the local grid instead of the UTM data.

The UTM to Lat/Lon and Lat/Lon to UTM conversion formulas were taken as-is from the
excellent article by Prof.Steven Dutch of the University of Wisconsin at Green Bay:
	http:#www.uwgb.edu/dutchs/UsefulData/UTMFormulas.htm

The (abridged) Molodensky transformations were taken from
	http:#home.hiwaay.net/~taylorc/bookshelf/math-science/geodesy/datum/transform/molodensky/
and can be found in many sources on the net.

Additional sources:
===================
1. dX,dY,dZ values:  http:#www.geo.hunter.cuny.edu/gis/docs/geographic_transformations.pdf

2. ITM data:  http:#www.mapi.gov.il/geodesy/itm_ftp.txt
   for the meridional arc false northing, the value is given at
   http:#www.mapi.gov.il/reg_inst/dir2b.doc	
   (this doc also gives a different formula for Lat/lon -> ITM, but not the reverse)

3. ICS data:  http:#www.mapi.gov.il/geodesy/ics_ftp.txt
   for the meridional arc false northing, the value is given at several places as the 
   correction value for Garmin GPS sets, the origin is unknown.
   e.g. http:#www.idobartana.com/etrexkb/etrexisr.htm

4. Israel center of mappings [govmap](https://govmap.gov.il/)