from shapely.geometry import shape


__author__ = 'spousty'

from fiona import collection
from pyproj import transform, Proj

import logging
import pdb

def projectPolygon(fromProj, toProj, inputGeom):
    try:
        new_coords = []
        for ring in inputGeom:
            try:
                x2, y2 = transform(fromProj, toProj, *zip(*ring))
                new_coords.append(zip(x2, y2))
            except TypeError as te:
                print te.message
        return new_coords
    except Exception, e:
        logging.exception("Error transforming feature %s:", new_coords)




#def projectLine(fromProj, toProj, inputGeom):



#def projectPoint(fromProj, toProj, inputGeom):


def getIntersections(clip, toBeClipped, outputDir):
    '''
    This method uses shapely's intersects method and saves the files out to an output directory.
    Here is the definition of intersects in shapely:
    "Returns True if the boundary and interior of the object intersect in any way with those of the other."
    '''

    featuresToWrite = []

    #read the both files in using fiona
    with collection(clip, "r") as clipColl:
        schema = clipColl.schema.copy()

        with collection(toBeClipped) as toBeClippedColl:
            print toBeClippedColl.name
            geomType = toBeClippedColl.schema['geometry']
            ##create our output shapefile
            outPath =  outputDir + '/' + toBeClippedColl.name + '_final.shp'
#            outputFile = collection(outPath, 'w', 'ESRI Shapefile', toBeClippedColl.schema.copy, {'init': 'epsg=4326', 'no_defs': True}  )

            with collection(outPath, 'w', 'ESRI Shapefile', toBeClippedColl.schema.copy(), {'init': 'epsg:4326'} ) as output:

                for clipFeature in clipColl:

                    for toBeClippedFeature in toBeClippedColl:
                        clipShape = shape(clipFeature['geometry'])
                        toBeClippedShape = shape(toBeClippedFeature['geometry'])
                        if clipShape.intersects(toBeClippedShape):
                            featureGeom = toBeClippedFeature['geometry']['type']
                            #winner winner chicken dinner the shapes intersect

                            if featureGeom =='Polygon':
                                newPolygonCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])
                               # print str(type(newPolygonCoords)) + " :: " +str(newPolygonCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygonCoords
                                output.write(toBeClippedFeature)

                            elif featureGeom == 'MultiPolygon':
                                ##need to split the geometry and put it back together before saving
                                newPolygons = []
                                for geom in toBeClippedFeature['geometry']['coordinates']:
                                    #print str(type(geom)) + " :: " +str(geom)
                                    newSinglePolyCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),geom)
                                    newPolygons.append(newSinglePolyCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygons
                                print toBeClippedFeature['id']
                                try:
                                    output.write(toBeClippedFeature)
                                    output.flush()
                                except Exception, e:
                                    print e.message


                            elif featureGeom =='LineString':
                                True
                            elif featureGeom == 'MultiLineString' :
                                True
                            elif featureGeom == 'Point':
                                True
                            else:
                                try:
                                    print '!!!!!!!!!!!!!!' + featureGeom
                                except:
                                    pdb.set_trace()
                                raise


