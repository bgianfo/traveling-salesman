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

def rand_seq(size):
    '''generates values in random order
    equivalent to using shuffle in random,
    without generating all values at once'''
    values=range(size)
    for i in xrange(size):
        # pick a random index into remaining values
        j=i+int(random.random()*(size-i))
        # swap the values
        values[j],values[i]=values[i],values[j]
        # return the swapped value
        yield values[i]

def all_pairs(size):
    '''generates all i,j pairs for i,j from 0-size'''
    for i in rand_seq(size):
        for j in rand_seq(size):
            yield (i,j)

def reversed_sections(tour):
    '''generator to return all possible variations where the section between two cities are swapped'''
    for i,j in all_pairs(len(tour)):
        if i != j:
            copy=tour[:]
            if i < j:
                copy[i:j+1]=reversed(tour[i:j+1])
            else:
                copy[i+1:]=reversed(tour[:j])
                copy[:j]=reversed(tour[i+1:])
            if copy != tour: # no point returning the same tour
                yield copy

def swapped_cities(tour):
    '''generator to create all possible variations where two cities have been swapped'''
    for i,j in all_pairs(len(tour)):
        if i < j:
            copy=tour[:]
            copy[i],copy[j]=tour[j],tour[i]
            yield copy

def cartesian_matrix(coords):
    '''create a distance matrix for the city coords that uses straight line distance'''
    matrix={}
    for i,(x1,y1) in enumerate(coords):
        for j,(x2,y2) in enumerate(coords):
            dx,dy=x1-x2,y1-y2
            dist=sqrt(dx*dx + dy*dy)
            matrix[i,j]=dist
    return matrix

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


def tour_length(matrix,tour):
    '''total up the total length of the tour based on the distance matrix'''
    total=0
    num_cities=len(tour)
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        total+=matrix[city_i,city_j]
    return total

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

def init_random_tour(tour_length):
   tour=range(tour_length)
   random.shuffle(tour)
   return tour

def run_hillclimb(init_function,move_operator,objective_function,max_iterations,coords):
    from hillclimb import hillclimb_and_restart
    iterations,score,best=hillclimb_and_restart(init_function,move_operator,objective_function,max_iterations,coords)
    return iterations,score,best

def run_anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha,coords):
    if start_temp is None or alpha is None:
        usage();
        print "missing --cooling start_temp:alpha for annealing"
        sys.exit(1)
    from sa import anneal
    iterations,score,best=anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha,coords)
    return iterations,score,best

def usage():
    print "usage: python %s [-o <output image file>] [-v] [-m reversed_sections|swapped_cities] -n <max iterations> [-a hillclimb|anneal] [--cooling start_temp:alpha] <city file>" % sys.argv[0]

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], "ho:vm:n:a:", ["cooling="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    out_file_name=None
    max_iterations=None
    verbose=None
    move_operator=reversed_sections
    run_algorithm=run_hillclimb
    coords = []
    
    start_temp,alpha=None,None
    
    for option,arg in options:
        if option == '-v':
            verbose=True
        elif option == '-h':
            usage()
            sys.exit()
        elif option == '-o':
            out_file_name=arg
        elif option == '-n':
            max_iterations=int(arg)
        elif option == '-m':
            if arg == 'swapped_cities':
                move_operator=swapped_cities
            elif arg == 'reversed_sections':
                move_operator=reversed_sections
        elif option == '-a':
            if arg == 'hillclimb':
                run_algorithm=run_hillclimb
            elif arg == 'anneal':
                # do this to pass start_temp and alpha to run_anneal
                def run_anneal_with_temp(init_function,move_operator,objective_function,max_iterations,coords):
                    return run_anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha,coords)
                run_algorithm=run_anneal_with_temp
        elif option == '--cooling':
            start_temp,alpha=arg.split(':')
            start_temp,alpha=float(start_temp),float(alpha)
    
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
    init_function=lambda: init_random_tour(len(coords))
    matrix=cartesian_matrix(coords)
    objective_function=lambda tour: -tour_length(matrix,tour)
    
    logging.info('using move_operator: %s'%move_operator)
    
    iterations,score,best=run_algorithm(init_function,move_operator,objective_function,max_iterations,coords)
    # output results
    print order(best)
    print iterations,score,best
    print str(calculatePathLen(best,coords)) + " mi"
    
if __name__ == "__main__":
    main()
