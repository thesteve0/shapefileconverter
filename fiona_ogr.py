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

        with collection(toBeClipped) as clippedColl:
            print clippedColl.name
            geomType = clippedColl.schema['geometry']
            ##create our output shapefile
            outPath =  outputDir + '/' + clippedColl.name + '_final.shp'
#            outputFile = collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy, {'init': 'epsg=4326', 'no_defs': True}  )

            with collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy(), {'init': 'epsg:4326'} ) as output:

                for clipFeature in clipColl:

                    for intersectCheck in clippedColl:
                        clipShape = shape(clipFeature['geometry'])
                        intersectShape = shape(intersectCheck['geometry'])
                        if clipShape.intersects(intersectShape):
                            featureGeom = intersectCheck['geometry']['type']
                            #winner winner chicken dinner the shapes intersect
                            #first project to our new geo

                            if 'Polygon' == featureGeom:
                                newPolygonCoords = projectPolygon(Proj(clippedColl.crs), Proj(output.crs),intersectCheck['geometry']['coordinates'])
                               # print str(type(newPolygonCoords)) + " :: " +str(newPolygonCoords)
                                intersectCheck['geometry']['coordinates'] = newPolygonCoords
                                output.write(intersectCheck)

                            elif 'MultiPolygon' == featureGeom:
                                ##need to split the geometry and put it back together before saving
                                newPolygons = []
                                intersectCheckBefore = intersectCheck.copy()
                                for geom in intersectCheck['geometry']['coordinates']:
                                    #print str(type(geom)) + " :: " +str(geom)
                                    newSinglePolyCoords = projectPolygon(Proj(clippedColl.crs), Proj(output.crs),geom)
                                    newPolygons.append(newSinglePolyCoords)
                                intersectCheck['geometry']['coordinates'] = newPolygons
                                try:
                                    output.write(intersectCheck)
                                except:
                                    pdb.set_trace()
                                    raise

                            elif 'LineString' == featureGeom:
                                True
                            elif 'MultiLineString' == featureGeom:
                                True
                            elif 'Point' == featureGeom:
                                True
                            else:
                                try:
                                    print '!!!!!!!!!!!!!!' + featureGeom
                                except:
                                    pdb.set_trace()
                                raise


