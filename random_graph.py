import networkx as nx
import random

random.seed(42)

def split_edge(G,e):
	n = len(G)
	assert G.has_edge(*e)
	G.remove_edge(*e)
	G.add_path([e[0], n, e[1]])
	assert len(G) == n+1
	return n

def random_3_edge_connected(n):
	""" Returns a random 3-edge connected MultiGraph"""

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

def make_simple(G):
	""" Makes a MultiGraph simple while preserving edge connectivity """
	def multi_edge_iter(G):
		"""Iterator over all multpile edges in the Graph. Yields (u,v,multiplicity)"""
		nodes = G.nodes()[:]
		for n in nodes:
			neighbors = sorted(map(lambda x: x[1], G.edges(n)))
			p = None
			repetitions = 0
			for u in neighbors:
				if u!=p:
					if repetitions >=1:
						yield n,p,repetitions+1
					p = u
					repetitions = 0
				else:
					repetitions += 1

	for e in G.selfloop_edges():
		G.remove_edge(*e)
	
	for (u,v,m) in multi_edge_iter(G):
		path = []
		for i in range(m):
			path.append(split_edge(G,(u,v)))
		G.add_path(path)

	simple = nx.Graph()
	simple.add_edges_from(G.edges())
	return simple
