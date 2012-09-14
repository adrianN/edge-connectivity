import networkx as nx
import random_graph as rg
from tests import *
from chain import *

def toStr(G):
	attr = nx.get_edge_attributes(G,'type')
	l = []
	for (u,v) in G.edges_iter():
		l.append(str(u)+'-'+str(v)+' '+str(attr[(u,v)]))
	return '\n'.join(l)

nx.Graph.__str__ = toStr


def dfs(G,source=None):
	"""Produce edges in a depth-first-search starting at source."""
	# Very slight modification of the DFS procedure from networkx
	if source is None:
		# produce edges for all components
		nodes=G
	else:
		# produce edges for components with source
		nodes=[source]
	visited=set()
	for start in nodes:
		if start in visited:
			continue
		visited.add(start)
		stack = [(start,iter(G[start]))]
		while stack:
			parent,children = stack[-1]
			try:
				child = next(children)
				if child not in visited:
					yield parent,child,'tree'
					visited.add(child)
					stack.append((child,iter(G[child])))
				else:
					yield parent,child,'back'
			except StopIteration:
				stack.pop()

def tree_path_edges(G,u,v):
	p = u
	while u!=v:
		u = p
		p = G.node[p]['parent']
		yield u,p

def tree_path_nodes(G,u,v):
	for x,y in tree_path_edges(G,u,v):
		yield x
	
	yield y

def direct_and_tag(G, source = None):
	""" Makes tree edges go up, back edges go down. Computes dfi, 
		parent for nodes and type (back, tree) for edges"""
	G2 = nx.DiGraph()
	G2.add_nodes_from(G.nodes_iter())
	positions = []
	seen = set()
	parent = dict.fromkeys(G2.nodes_iter())
	for (u,v,d) in dfs(G, source):
		if d=='tree':
			G2.add_edge(v,u, type=d) #tree edges go up
			parent[v] = u
		else:
			if not G2.has_edge(u,v):
				G2.add_edge(v,u, type=d) #back edges go down
				
		for x in (u,v):
			if not x in seen:
				seen.add(x)
				positions.append(x)

	depth_first_index = dict(map((lambda (x,y): (y,x)), enumerate(positions)))
	nx.set_node_attributes(G2,'dfi',depth_first_index)
	nx.set_node_attributes(G2,'parent',parent)
	nx.set_node_attributes(G2,'real', dict.fromkeys(G2.nodes_iter(), False))

	return G2




def chain_decomposition(G, source = None):
	""" Decomposes G into chains. The first three chains form a K23.
		Assigns a chain to every edge.
		Returns a list of chains."""
	if source == None:
		source = (G.nodes_iter()).next()

	G = direct_and_tag(G, source)
	check_basic_information(G)

	for u,v in G.edges():
		print u,v, G[u][v]

	chains = find_k23(G, source)
	chain_number = 3
	for x in nx.dfs_preorder_nodes(G,source):
		for u in G.successors(x):
			chain = [x]
			while not 'chain' in G[chain[-1]][u]:
				chain.append(u)
				u = G.node[u]['parent']

			if len(chain)>1:
				G.add_path(chain, chain = chain_number)
				start, first_node, last_node, parent = chain[0], chain[1], chain[-1], G[chain[-1]][u]['chain']
				chains.append(Chain(
						G,
						start,
						first_node,
						last_node,
						parent,
						classify_chain(G, start, chains[parent]),
						chains))
				chain_number = chain_number + 1

	check_chain_decomposition(G, chains)

	return chains

def classify_chain(G, s, p):
	""" Classifies chains into three types.
		1. start and end are contained in the parent chain
		2. start == start(parent)
		3. Otherwise
		Chain 0 is a special case and has type None
	"""
	dfi = nx.get_node_attributes(G,'dfi')

	if s == p.start: 
		return 2
	elif dfi[s] >= dfi[p.end]:
		return 1
	else:
		return 3


def find_k23(G, source):
	succ = G.successors(source)
	cycle = set()
	cycle.add(source)

	#find a basic cycle
	s = succ[0]
	while s!=source:
		cycle.add(s)
		s = G.node[s]['parent']

	#find a second chain
	for s in succ[1:]:
		t = s
		while not t in cycle:
			t = G.node[t]['parent']
		if not t == source:
			break

	assert not t == source, "Graph is not 3-edge connected"

	# source, succ[0], s, t define a k23
	#mark the initial three chains
	chains = [[],[source],[source]]

	for i, x, stop in (0, t, source), (1, succ[0], t), (2, s, t):
		while x!=stop:
			chains[i].append(x)
			x = G.node[x]['parent']
		chains[i].append(stop)
		G.add_path(chains[i], chain=i)

	C = []
	C.append(Chain(G, chains[0][0], chains[0][1], chains[0][-1], None, None, None))
	C.append(Chain(G, chains[1][0], chains[1][1], chains[1][-1], 0, 2, C))
	C.append(Chain(G, chains[2][0], chains[2][1], chains[2][-1], 0, 2, C))
	map(lambda x: x.add(), C)
	return C

def add_chains(G, chains):
	for chain in chains:
		assert chain.is_added
		#all type 2 chains can be added, since chain.start is real
		for child in chain.children2:
			child.is_added=True



G = rg.make_simple(rg.random_3_edge_connected(100))
G2 = chain_decomposition(G)
print map(str,G2)