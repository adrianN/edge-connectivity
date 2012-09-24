import networkx as nx
import random

random.seed(42)

def split_edge(G,e):
	n = len(G)
	while n in G: n += 1
	assert G.has_edge(*e)
	G.remove_edge(*e)
	G.add_path([e[0], n, e[1]])
	return n

def random_3_edge_connected(n):
	""" Returns a random 3-edge connected MultiGraph with roughly n nodes"""

	def add_edge(G):
		u = random.choice(G.nodes())
		v = random.choice(G.nodes())
		G.add_edge(u,v)

	def subdivide_edge(G):
		u = random.choice(G.nodes())
		e = random.choice(G.edges())
		v = split_edge(G, e)
		G.add_edge(v,u)

	def subdivide_two_edges(G):
		e1, e2 = random.sample(G.edges(),2)
		a = split_edge(G, e1)
		b = split_edge(G, e2)
		G.add_edge(a,b)
		

	G = nx.MultiGraph()
	G.add_path([0,1])
	G.add_path([0,1])
	G.add_path([0,1])

	functions = add_edge, subdivide_edge, subdivide_two_edges
	while len(G)<n-1:
		random.choice(functions)(G)

	return G

def glue_graphs(G,G2,k):
	"""Connect two graphs by k edges, return a new graph"""
	v = [random.choice(G.nodes()) for i in range(k)]
	v2 = [random.choice(G2.nodes()) for i in range(k)]
	newG = nx.MultiGraph()
	d = [dict(),dict()]
	for i,x in enumerate(G.nodes()):
		d[0][x] = i
	for i,x in enumerate(G2.nodes()):
		d[1][x] = i+len(G)

	for (x,y) in G.edges():
		newG.add_edge(d[0][x], d[0][y])
	for (x,y) in G2.edges():
		newG.add_edge(d[1][x], d[1][y])

	print 'cut',
	for i in range(len(v)):
		newG.add_edge(d[0][v[i]], d[1][v2[i]])
		print (d[0][v[i]], d[1][v2[i]]),
	print
	return newG

def not_3_conn(n):
	"""Returns a graph with roughly n nodes containing two subgraphs that can be separated by up to two edges"""
	G = random_3_edge_connected(max(4,n/2))
	G2 = random_3_edge_connected(max(4,n-len(G)))
	k = random.choice([1,2])
	print 'this graph is',k,'connected'
	nG = glue_graphs(G,G2,k)
	assert nx.is_connected(nG)
	return nG

def make_simple(G):
	""" Makes a MultiGraph simple while preserving edge connectivity """
	def multi_edge_iter(G):
		"""Iterator over all multpile edges in the Graph. Yields (u,v,multiplicity)"""
		nodes = G.nodes()[:]
		for n in nodes:
			for u in G.neighbors(n):
				if G.number_of_edges(n,u) > 1:
					yield (n,u,G.number_of_edges(n,u))


	for e in G.selfloop_edges():
		G.remove_edge(*e)
	
	for (u,v,m) in multi_edge_iter(G):
		path = []
		for i in range(max(2,m-1)):
			path.append(split_edge(G,(u,v)))
		G.add_path(path)

	simple = nx.Graph()
	simple.add_edges_from(G.edges())
	return simple
