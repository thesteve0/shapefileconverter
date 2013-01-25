from glob import glob
import os
from shapely.geometry import shape


__author__ = 'spousty'

from fiona import collection
from pyproj import transform, Proj

import logging


def getIntersections(clip, toBeClipped, outputDir):
    '''
    This method uses shapely's intersects method and saves the files out to an output directory.
    Here is the definition of intersects in shapely:
    "Returns True if the boundary and interior of the object intersect in any way with those of the other."
    '''

    filesToDelete = [ ]

    #read the both files in using fiona
    #This collection is the feature(s) that will be used to select the other features
    with collection(clip, "r") as clipColl:
        schema = clipColl.schema.copy()

        #This collection are the features that will be selected
        with collection(toBeClipped) as toBeClippedColl:
            print toBeClippedColl.name
            geomType = toBeClippedColl.schema['geometry']


            ##create our output shapefile
            outPath =  outputDir + '/' + toBeClippedColl.name + '_final.shp'

            #because OGR only allows one geom type to be written to a file, we are going to coerce everything to
            #Multi (ie Polygon -> Multipolygon)
            newSchema = toBeClippedColl.schema.copy()
            if 'Polygon' == newSchema['geometry']:
                newSchema['geometry'] = 'MultiPolygon'
            elif 'LineString' == newSchema['geometry']:
                newSchema['geometry'] = 'MultiLineString'
            ##There are no multipoints in these data sets otherwise we would have to do the same thing


            with collection(outPath, 'w', 'ESRI Shapefile', newSchema, {'init': 'epsg:4326'} ) as output:

                for clipFeature in clipColl:

                    for toBeClippedFeature in toBeClippedColl:
                        clipShape = shape(clipFeature['geometry'])
                        toBeClippedShape = shape(toBeClippedFeature['geometry'])
                        if clipShape.intersects(toBeClippedShape):

                            #winner winner chicken dinner the shapes intersect
                            featureGeom = toBeClippedFeature['geometry']['type']

                            if featureGeom =='Polygon':
                                #Need to make these into Multipolygons
                                newPolygons = []
                                newPolygonCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])
                                newPolygons.append(newPolygonCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygons
                                toBeClippedFeature['geometry']['type'] = 'MultiPolygon'
                                output.write(toBeClippedFeature)

                            elif featureGeom == 'MultiPolygon':
                                ##need to split the geometry and put it back together before saving
                                newPolygons = []
                                for geom in toBeClippedFeature['geometry']['coordinates']:
                                    newSinglePolyCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),geom)
                                    newPolygons.append(newSinglePolyCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygons
                                output.write(toBeClippedFeature)


                            elif featureGeom =='LineString':

                                newMultiLineCoords  = [ ]
                                ## Need to make these into MultiLineStrings
                                toBeClippedFeature['geometry']['type'] = 'MultiLineString'
                                newLineCoords = projectLine(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])
                                newMultiLineCoords.append(newLineCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newMultiLineCoords

                                try:
                                        output.write(toBeClippedFeature)
                                except:
                                        print "in the exception"

                            elif featureGeom == 'MultiLineString':
                                print "in multilinestring"
                                newMultiLineCoords  = [ ]
                                for lineString in toBeClippedFeature['geometry']['coordinates']:
                                    newLineCoords = projectLine(Proj(toBeClippedColl.crs), Proj(output.crs), lineString)
                                    newMultiLineCoords.append(newLineCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newMultiLineCoords
                                output.write(toBeClippedFeature)

                            elif featureGeom == 'Point':
                                newPointCoords = projectPoint(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])
                                toBeClippedFeature['geometry']['coordinates'] = newPointCoords
                                output.write(toBeClippedFeature)
                            else:
                                print '!!!!!! ERROR - unexpected Geometry type !!!!!!!!' + featureGeom
            #if there are 0 features in the output then there are no intersecting features and we should delete the output file
            if len(output) < 1:
                print "should remove " + output.name
                filesToDelete.append(output.name)

    #all done time to delete our emptyfiles - remember a shapefile actually contains many files
    for shapeFile in filesToDelete:
        for fileName in glob(outputDir + "/" + shapeFile + "*"):
            os.remove(fileName)


def projectPoint(fromProj, toProj, inputGeom):
    ''' in each of these function we need to "unpack" the geometries to a lesser or greater degree. Points
     need the least amount of unpacking to work in the transform function (which does the actual projecting). Then
     We just return the geometry
    '''
    try:
        x2, y2 = transform(fromProj, toProj, inputGeom[0], inputGeom[1])
        pointTuple = (x2, y2)
        return pointTuple
    except Exception, e:
        logging.exception("Error transforming feature %s:", str(e))


def projectPolygon(fromProj, toProj, inputGeom):
    try:
        new_coords = []
        for ring in inputGeom:
            x2, y2 = transform(fromProj, toProj, *zip(*ring))
            new_coords.append(zip(x2, y2))
        return new_coords
    except Exception, e:
        logging.exception("Error transforming feature %s:", new_coords)


def projectLine(fromProj, toProj, inputGeom):
    try:
        x2, y2 = transform(fromProj, toProj, *zip(*inputGeom))
        return zip(x2, y2)
    except Exception, e:
        logging.exception("Error transforming feature %s:", new_coords)




