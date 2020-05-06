# the functions to be exposed as a web service

import automap as mapfit
from PIL import Image

import sys, io, codecs
import urllib
import json

def transform_geoj(geoj, trans):
    # NOTE: changes the geoj in-place
    trans = mapfit.transforms.from_json(trans)

    # process
    def ring_trans(coords):
        x,y = zip(*coords)
        newx,newy = trans.predict(x, y)
        newcoords = list(zip(newx, newy))
        return newcoords

    def geom_trans(geoj, trans):
        typ = geoj['type']
        
        if typ == 'Point':
            geoj['coordinates'] = ring_trans([geoj['coordinates']])[0]
            
        elif typ in ('MultiPoint','LineString'):
            geoj['coordinates'] = ring_trans(geoj['coordinates'])
            
        elif typ in ('MultiLineString','Polygon'):
            parts = []
            for part in geoj['coordinates']:
                part = ring_trans(part)
                parts.append(part)
            geoj['coordinates'] = parts
            
        elif typ == 'MultiPolygon':
            polys = []
            for poly in geoj['coordinates']:
                parts = []
                for part in poly:
                    part = ring_trans(part)
                    parts.append(part)
                polys.append(parts)
            geoj['coordinates'] = polys
            
        else:
            raise Exception('Unknown GeoJSON type "{}"'.format(typ))
        
        return geoj

    typ = geoj['type']
    
    if typ == 'FeatureCollection':
        for feat in geoj['features']:
            feat['geometry'] = geom_trans(feat['geometry'], trans)
            
    elif typ == 'GeometryCollection':
        geoms = []
        for geom in geoj['geometries']:
            geom = geom_trans(geom, trans)
            geoms.append(geom)
        geoj['geometries'] = geoms
        
    else:
        geoj = geom_trans(geoj, trans)
        
    return geoj

# test
# http://localhost:8000/map/view/68/georef
##trans = {"params": {"order": 2},
##         "type": "Polynomial",
##         "data": {"A": [[-3.856139612923584e-08, -2.559536029038356e-07, -5.013052748942585e-09, 0.006979262757356154, 0.00015264777089216413, -18.218350320739596], [-1.6173470463930547e-07, 5.9587620755410044e-08, 4.149854740293216e-08, 0.0001316740373948097, -0.006653705237171262, 18.643769517332938], [0.0, 0.0, 1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]]}}
##geoj = {'type':'LineString',
##        'coordinates':[(0,0),(1104,1292)]}
##print transform_geoj(geoj, trans)
##fdsfds

if __name__ == '__main__':
    # redirect all prints
    sys.stdout = codecs.getwriter('utf8')(io.BytesIO()) #io.TextIOWrapper(io.BytesIO(), encoding='utf8', errors='ignore')
    sys.stderr = codecs.getwriter('utf8')(io.BytesIO())

    # parse args
    print(sys.argv)
    geoj,trans = sys.argv[1],sys.argv[2]
    print(geoj, trans)
    trans = json.loads(trans)
    geoj = json.loads(geoj)

    # run
    result = transform_geoj(geoj, trans)
    #print(result)

    # return result json via normal stdout
    sys.__stdout__.write(json.dumps(result))
    


