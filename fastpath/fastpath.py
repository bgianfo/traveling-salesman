#!/usr/bin/python

import random
import sys
import getopt
from math import sqrt
import math

nauticalMilePerLat = 60.00721
nauticalMilePerLongitude = 60.10793
rad = math.pi / 180.0
milesPerNauticalMile = 1.15078

def read_coords(coord_file):
    '''
    read the coordinates from file and return the distance matrix.
    coords should be stored as comma separated floats, one x,y pair per line.
    '''
    coords=[]
    for line in coord_file:
        x,y=line.strip().split(',')
        coords.append((float(x),float(y)))
    return coords

def order(best):
    file = open('cities','r')
    cities = []
    for city in file:
      cities.append(city)

    file.close()

    for i in best:
      print cities[i]

def calcDistance(lat1, lon1, lat2, lon2):
  """
  Caclulate distance between two lat lons in NM
  """
  yDistance = (lat2 - lat1) * nauticalMilePerLat
  xDistance = (math.cos(lat1 * rad) + math.cos(lat2 * rad)) * (lon2 - lon1) * (nauticalMilePerLongitude / 2)
  distance = math.sqrt( yDistance**2 + xDistance**2 )
  return distance * milesPerNauticalMile

def calculatePathLen(path, arr):
  first = True
  lastpoint = ()
  length = 0
  for point in path:
    if first:
      lastpoint = point
      first = False
    else:
      length += calcDistance(arr[lastpoint][0],arr[lastpoint][1],arr[point][0],arr[point][1])
      lastpoint = point

  return length

def usage():
    print "usage: python %s [-v] -n <max iterations> <city file>" % sys.argv[0]

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], "ho:vm:n:a:", ["cooling="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    max_iterations=None
    verbose=None
    for option,arg in options:
        if option == '-v':
            verbose=True
        elif option == '-h':
            usage()
            sys.exit()
        elif option == '-n':
            max_iterations=int(arg)

    if max_iterations is None:
        usage();
        sys.exit(2)

    if out_file_name and not out_file_name.endswith(".png"):
        usage()
        print "output image file name must end in .png"
        sys.exit(1)

    if len(args) != 1:
        usage()
        print "no city file specified"
        sys.exit(1)

    city_file=args[0]

    # enable more verbose logging (if required) so we can see workings
    # of the algorithms
    import logging
    format='%(asctime)s %(levelname)s %(message)s'
    if verbose:
        logging.basicConfig(level=logging.INFO,format=format)
    else:
        logging.basicConfig(format=format)

    # setup the things tsp specific parts hillclimb needs
    coords=read_coords(file(city_file))

    # output results
    print order(best)
    print iterations,score,best
    print str(calculatePathLen(best,coords)) + " mi"

if __name__ == "__main__":
    main()
