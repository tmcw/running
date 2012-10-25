The tools used to make [my running map](http://macwright.org/running/) - this
code will let you download runs from [Garmin Connect](http://connect.garmin.com/),
translate tcx files to Shapefiles en masse, and `squiggly.py` is the implementation
of the very custom 'squiggly' line-to-polygon creator.

## Usage

These tools require [Shapely](http://pypi.python.org/pypi/Shapely),
[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/), [OGR](http://www.gdal.org/ogr/),
and a few other libraries to operate `disconnect.rb`.

## License

`tcx2shp.py` was originally written by [Matthew Perry](http://blog.perrygeo.net/)
and thus has an Apache License.

Everything else is 3-clause BSD.
