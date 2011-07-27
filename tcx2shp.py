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

def parse_tcx3(infile, lyr):
    soup = bss(open(infile,'r'))

    # Activity
    for activity in soup.findAll('activity'):
        sport = activity['sport']
        activityid = activity.id.string

        # Lap
        for lap in activity.findAll('lap'):
            # Track
            for track in lap.findAll('track'):

                # Trackpoint
                for point in track.findAll('trackpoint'):
                    feature = {}
                    pointid = point.time.string
                    feature['time'] = time_code(pointid)
                    feature['activityid'] = time_code(activityid)
                    try:
                        feature['speed'] = float(point.find('ns3:speed').string)
                    except: feature['speed'] = 0

                    try:
                        feature['coords'] = [float(x) for x in
                                 [point.position.longitudedegrees.string,
                                  point.position.latitudedegrees.string]]
                    except: coords = None

                    try: feature['alt'] = float(point.altitudemeters.string)
                    except: feature['alt'] = 0

                    try: feature['bpm'] = int(point.heartratebpm.value.string)
                    except: feature['bpm'] = 0

                    add_feature(lyr, feature)

def setup_shapefile(ds):
    lyr = ds.CreateLayer('points')

    numfields = ['bpm', 'alt', 'speed']
    stringfields = ['time', 'activityid']

    for i in numfields:
        field_defn = ogr.FieldDefn(i, ogr.OFTReal )
        lyr.CreateField(field_defn)

    for i in stringfields:
        field_defn = ogr.FieldDefn(i, ogr.OFTString )
        field_defn.SetWidth(256)
        lyr.CreateField(field_defn)


    return lyr

def add_feature(lyr, feature):
    if (feature.has_key('coords')):
        feat = ogr.Feature(lyr.GetLayerDefn())
        feat.SetField(0, feature['bpm'])
        feat.SetField(1, feature['alt'])
        feat.SetField(2, feature['speed'])
        feat.SetField(3, feature['time'])
        feat.SetField(4, feature['activityid'])
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.SetPoint_2D(0, feature['coords'][0], feature['coords'][1])
        feat.SetGeometry(pt)
        lyr.CreateFeature(feat)

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

    vector = ogr.GetDriverByName(options.format)
    ds = vector.CreateDataSource(outfile)
    lyr = setup_shapefile(ds)

    for infile in infiles:
        tcx = parse_tcx3(infile, lyr)
