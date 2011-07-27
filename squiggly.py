#!/usr/bin/python

import shapely
from shapely import speedups, wkb
from shapely.geometry import LineString, Point
from osgeo import ogr
from optparse import OptionParser
from math import atan2, degrees, sin, cos
import math

# Be fast if possible.
if shapely.speedups.available:
    shapely.speedups.enable()

parser = OptionParser(usage='%prog SCALE_FIELD output.shp input.shp')
parser.add_option('-m', '--max-offset', dest='max_offset', default=2000.0)

# Plug Shapely and OGR into each other and hope it works.
def load_shapefile(filename, scale_field):
    # Abstracting these calls into another function
    # will segfault due to Python/OGR fights
    try:
        source = ogr.Open(filename)
        l = source.GetLayer(0)
    except:
        raise Exception('Error opening input file')

    f = l.GetNextFeature()
    if not f:
        raise Exception('empty shapefile found')
    f = f.Clone()
    while f:
        # yielding here in an early attempt to avoid
        # putting everything in memory. But since we're dealing
        # with min/max measures, that's not a possibility, yet.
        yield [f.GetField(scale_field),
                shapely.wkb.loads(f.GetGeometryRef().ExportToWkb()),
                f.GetField('speed')]
        f = l.GetNextFeature()
        f = f.Clone() if f else False

def angle(a, b):
    return atan2(
        a.coords[0][1] - b.coords[0][1],
        a.coords[0][0] - b.coords[0][0])

def translate(e, scale_factor, point, max_offset):
    # now project outwards.
    x = cos(e)
    y = sin(e)
    # And scale by our spot in the feature
    x = x * scale_factor * (1.0 / max_offset)
    y = y * scale_factor * (1.0 / max_offset)
    # and translate
    p = point
    return Point((p.coords[0][0] + x, p.coords[0][1] + y))

def average_smooth_n(x, n=5):
    weight = 0.7
    for i in range(n, len(x) - 1):
        before = x[i - n:i - 1]

        def get_x(m):
            return m[1].coords[0][0]

        def get_y(m):
            return m[1].coords[0][1]

        before_x = sum(map(get_x, before)) / (n - 1)
        before_y = sum(map(get_y, before)) / (n - 1)

        x[i][1].coords = [(
            x[i][1].coords[0][0] * weight + before_x * (1 - weight),
            x[i][1].coords[0][1] * weight + before_y * (1 - weight)
        )]

    return x

def make_breaks(l, n):
    l.sort()
    step = int(len(l) / n)
    return [l[step * i] for i in range(n)]

def get_break(v, breaks):
    if v <= breaks[0]:
        return 0;
    if v >= breaks[-1]:
        return len(breaks);
    for x in range(len(breaks)):
        if breaks[x] > v:
            return x + 1

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    if len(args) < 2:
        exit(parser.print_usage())

    (scale_field, infile, outfile) = args

    features = average_smooth_n([x for x in load_shapefile(infile, scale_field)])

    scale_values = [x[0] for x in features]

    n_breaks = 10
    breaks = make_breaks(scale_values, n_breaks)

    left_points = []
    factors = []
    speeds = []
    right_points = []

    for i in range(1, len(features)):
        # Dividing by zero is no good, guys!
        scale_factor = (get_break(features[i][0], breaks) + 1) / float(n_breaks)

        # Angle can only be determined later.
        if i == 1:
            # The angle of the first line segment is only
            # based on it and the first point
            a = angle(features[0][1], features[1][1])
        else:
            # All following line segments are calculated
            # with the segment preceding and following
            j = angle(features[i - 2][1], features[i - 1][1])
            k = angle(features[i - 1][1], features[i][1])
            a = (j + k) / 2

        factors.append(features[i - 1][0])
        speeds.append(features[i - 1][2])
        left_points.append(translate(a + 90, scale_factor,
            features[i - 1][1], options.max_offset))
        right_points.append(translate(a - 90, scale_factor,
            features[i - 1][1], options.max_offset))

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')

    squiggle_ds = shpdriver.CreateDataSource(outfile)
    lyr = squiggle_ds.CreateLayer('squiggle')

    field_defn = ogr.FieldDefn(scale_field, ogr.OFTReal)
    lyr.CreateField(field_defn)

    field_defn = ogr.FieldDefn('speed', ogr.OFTReal)
    lyr.CreateField(field_defn)

    t = 2

    for i in range(t, len(features) - 1, t):
        quadpoints = left_points[i].union(right_points[i])

        for j in range(i - t, i + 1):
            quadpoints = quadpoints.union(left_points[j])
            quadpoints = quadpoints.union(right_points[j])

        quadrilateral = quadpoints.convex_hull
        q_geom = ogr.CreateGeometryFromWkb(quadrilateral.wkb)
        q_feature = ogr.Feature(lyr.GetLayerDefn())
        q_feature.SetGeometry(q_geom)
        q_feature.SetField(0, factors[i])
        q_feature.SetField(1, speeds[i])
        lyr.CreateFeature(q_feature)
