from shapely.geometry import shape

__author__ = 'spousty'

from fiona import collection
from pyproj import transform

import pprint
import logging

def projectPolygon(fromProj, toProj, inputFeature, outFile):

    #TODO Rewrite to handle a single feature
    try:
        new_coords = []
        for ring in inputFeature['geometry']['coordinates']:
            x2, y2 = transform(fromProj, toProj, *zip(*ring))
            new_coords.append(zip(x2, y2))
        inputFeature['geometry']['coordinates'] = new_coords
        outFile.write(f)

    except Exception, e:
        # Writing uncleanable features to a different shapefile
        # is another option.
        logging.exception("Error transforming feature %s:", inputFeature['id'])




#def projectLine(fromProj, toProj, inputFeature):



#def projectPoint(fromProj, toProj, inputFeature):


def getIntersections(clip, toBeClipped, outputDir):
    '''
    This method uses shapely's intersects method and saves the files out to an output directory.
    Here is the definition of intersects in shapely:
    "Returns True if the boundary and interior of the object intersect in any way with those of the other."
    '''

    featuresToWrite = []

    #read the both files in using fiona
    with collection(clip, "r") as clipColl:
#        pprint.pprint(clipColl.crs, indent=4)
        schema = clipColl.schema.copy()
#            print clipColl.crs
#            print len(clipColl)

        with collection(toBeClipped) as clippedColl:

            pprint.pprint(clippedColl.schema['geometry'], indent=4)
            geomType = clippedColl.schema['geometry']

            ##create our output shapefile
            outPath =  outputDir + '/' + clippedColl.name + '_final.shp'
#            outputFile = collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy, {'init': 'epsg=4326', 'no_defs': True}  )
            with collection(outPath, 'w', 'ESRI Shapefile', clippedColl.schema.copy, {'init': 'epsg:4326'} ) as output:

                for clipFeature in clipColl:

                    for intersectCheck in clippedColl:
                        clipShape = shape(clipFeature['geometry'])
                        intersectShape = shape(intersectCheck['geometry'])
                        if clipShape.intersects(intersectShape):
                            #winner winner chicken dinner the shapes intersect
                            #first project to our new geo
                            if geomType == 'Polygon':
                                projectPolygon(Proj(clippedColl.crs), Proj(output.crs), intersectCheck, output)
                            elif geomType == 'LineString':
                                True
                            elif geomType == 'Point':
                                True
                            else:
                                print " ***** Found a geom type we weren't expecting: " + geomType



                            #then add to the array to write
                           # featuresToWrite.append(intersectShape)

