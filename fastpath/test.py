import random
import sys

INFINITE=1000000000

class Node:
  def __init__(self, pos, open=True):
    assert(len(pos)==2)
    self.pos = pos        #where this node is located
    self.neighbours = []    #a list of all neighbour nodes
    self.open = open      #True if this node is traversable
    self.distance = 0     #distance to the startnode
    self.visited = False    #True if this node has already been visited this run
    self.visited_from = None  # the tile we came from when calculating distance, not needed as were not interested in the path 

  def __repr__(self):
    s = "pos: "+str(self.pos)
    s += "\nopen: "+str(self.open)
    s += "\ndistance: "+str(self.distance)
    s += "\nvisited: "+str(self.visited)
    return s

  def add_neighbour(self, n):
    if not n in self.neighbours and n is not self and self.open and n.open:
      self.neighbours.append(n)

class Graph:
  def __init__(self):
    self.nodes = []
    self.longest_distance = (0,None,None) #three element tuple; distance, node1, node2

  def add_node(self, x, y):
    self.nodes.append(Node((x,y)))

  def find_node(self, pos):
    for i in self.nodes:
      if i.pos==pos:
        return i
    return None

  def reset(self, startpos):
    for i in self.nodes:
      i.distance = INFINITE
      i.visited = False

  def calc_neighbours(self):
    print "calculating neigbours"
    for i in self.nodes:
      for p in self.nodes:
          i.add_neighbour(p)

  def dijkstra(self, startpos):
    print "running dijkstra from",startpos
    self.reset(startpos)
    current = self.find_node(startpos)
    current.distance = 0

    #run as long as we have nodes to visit
    while current:
      for i in current.neighbours:
        if not i.visited:
          dist = current.distance+1
          if dist < i.distance:
            i.distance = dist
            i.visited_from = current
      current.visited = True
      current = self.find_next_unvisited()

    #update longest distance
    longest = None
    for i in self.nodes:
      if longest==None or i.distance > longest.distance:
        longest = i
    if longest.distance > self.longest_distance[0]:
      self.longest_distance = (longest.distance, self.find_node(startpos), longest)

  def calc_longest_distance(self):
    #run dijkstra on every node, each run will overwrite self.longest_distance
    for i in self.nodes:
      if i.open:
        self.dijkstra(i.pos)

  def find_next_unvisited(self):
    best = None
    for i in self.nodes:
      if not i.visited:
        if best==None or i.distance < best.distance:
          best = i
    return best

  def calc_bounds(self):
    x,y = 0,0
    for i in self.nodes:
      if i.pos[0]>x: 
        x = i.pos[0]
      if i.pos[1]>y: 
        y = i.pos[1]
    return x,y

  def ascii_repr(self):
    s = ""
    b = self.calc_bounds()
    for y in range(b[1]):
      for x in range(b[0]):
        n = self.find_node((x,y))
        if n and n.open:
          s += "."
        else:
          s += "#"
      s += "\n"
    return s

def add_nodes(g, sx, sy):
  #create nodes in a square
  for y in range(sy):
    for x in range(sx):
      g.add_node(x, y)

def block_random_nodes(g, num):
  #set node.open to false on random nodes
  b = g.calc_bounds()
  for i in range(num):
    x = int(random.random()*b[0])
    y = int(random.random()*b[1])
    g.find_node((x,y)).open = False

def addNodes(graph):
  file = open(sys.argv[1],'r')
  coords=[]
  for line in file:
      x,y=line.strip().split(',')
      coords.append((float(x),float(y)))

  for point in coords:
    graph.add_node(point[0],point[1])

def main():
  #create and display a graph
  graph = Graph()
  addNodes(graph)
  #print graph.ascii_repr()

  #run dijkstra
  graph.calc_neighbours()
  #g.dijkstra((0,0))
  graph.calc_longest_distance()

  #done
  for g in graph.longest_distance:
    print g

  print "best distance (",graph.longest_distance[0],") is between"
  print graph.longest_distance[1].pos,"and",graph.longest_distance[2].pos

if __name__=="__main__":
  main()

