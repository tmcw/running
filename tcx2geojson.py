#!/usr/bin/python

"""
Modified by Tom MacWright 2011

Author: Matthew Perry
Copyright 2008 Matthew T. Perry

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
from osgeo import ogr
from optparse import OptionParser
from BeautifulSoup import BeautifulStoneSoup as bss
from shapely.geometry import mapping, shape, LineString
from shapely.ops import cascaded_union
from fiona import collection

def parse_tcx3(infiles):
    schema = { 'geometry': 'LineString', 'properties': {} }
    with collection(
        "lines.shp", "w", "ESRI Shapefile", schema) as output:
        for infile in infiles:
            print "processing %s" % infile
            soup = bss(open(infile,'r'))

            ls = []
            # Activity
            for activity in soup.findAll('activity'):

                # Lap
                for lap in activity.findAll('lap'):
                    # Track
                    for track in lap.findAll('track'):

                        # Trackpoint
                        for point in track.findAll('trackpoint'):
                            try:
                                coords = [float(x) for x in
                                         [point.position.longitudedegrees.string,
                                          point.position.latitudedegrees.string]]
                                ls.append(coords)
                            except: coords = None
            if len(ls) > 2:
                output.write({
                    'properties': {
                    },
                    'geometry': mapping(LineString(ls))
                })

def time_code(t):
    '''Parse a time & return seconds from epoch'''
    y = int(t[:4])
    m = int(t[5:7])
    day = int(t[8:10])
    h = int(t[11:13])
    minute = int(t[14:16])
    sec = int(t[17:19])
    timestamp = y,m,day,h,minute,sec,-1, -1, -1
    timeCode = time.mktime(timestamp)
    return timeCode

parser = OptionParser()
parser.add_option('-f', '--format', dest='format', help='OGR File Format',
        default='ESRI Shapefile')

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    outfile = args[0]
    infiles = args[1:]

    parse_tcx3(infiles)
