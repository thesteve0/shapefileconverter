from shapely.geometry import shape


__author__ = 'spousty'

from fiona import collection
from pyproj import transform, Proj

import logging

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


def projectLine(fromProj, toProj, inputGeom):
    print 'in projectLine'
    try:
        new_coords = []
        try:
            x2, y2 = transform(fromProj, toProj, *zip(*inputGeom))
            new_coords.append(zip(x2, y2))
        except TypeError as te:
            print te.message
        return new_coords
    except Exception, e:
        logging.exception("Error transforming feature %s:", new_coords)



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

            #because OGR only allows one geom type to be written to a file, we are going to coerce everything to
            #Multi (ie Polygon -> Multipolygon
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
                            featureGeom = toBeClippedFeature['geometry']['type']
                            #winner winner chicken dinner the shapes intersect

                            if featureGeom =='Polygon':
                                #Need to make these into Multipolygons
                                newPolygons = []
                                newPolygonCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])

                                #TODO how do I stop the writing of the file if there are no features in it

                                newPolygons.append(newPolygonCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygons
                                toBeClippedFeature['geometry']['type'] = 'MultiPolygon'
                                #output.write(toBeClippedFeature)

                            elif featureGeom == 'MultiPolygon':
                                ##need to split the geometry and put it back together before saving
                                newPolygons = []
                                for geom in toBeClippedFeature['geometry']['coordinates']:
                                    #print str(type(geom)) + " :: " +str(geom)
                                    newSinglePolyCoords = projectPolygon(Proj(toBeClippedColl.crs), Proj(output.crs),geom)
                                    newPolygons.append(newSinglePolyCoords)
                                toBeClippedFeature['geometry']['coordinates'] = newPolygons

                                #output.write(toBeClippedFeature)


                            elif featureGeom =='LineString':
                                ## Need to make these into MultiLineStrings
                                toBeClippedFeature['geometry']['type'] = 'MultiLineString'
                                newLineCoords = projectLine(Proj(toBeClippedColl.crs), Proj(output.crs),toBeClippedFeature['geometry']['coordinates'])

                                toBeClippedFeature['geometry']['coordinates'] = newLineCoords
                                #output.write(toBeClippedFeature)
                                True
                            elif featureGeom == 'MultiLineString' :
                                True
                            elif featureGeom == 'Point':
                                True
                            else:
                                print '!!!!!!!!!!!!!!' + featureGeom


