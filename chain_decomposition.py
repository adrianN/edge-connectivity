import networkx as nx
from tests import *
from chain import *
from conn_exceptions import ConnEx

def dfs(G,source=None):
	"""Produce edges in a depth-first-search starting at source. 
	Edges are tagged as either 'tree' or 'back'"""
	# Very slight modification of the DFS procedure from networkx
	# One could unify this with direct_and_tag, but it seemed cleaner this way
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


def direct_and_tag(G, source = None):
	""" Makes tree edges go up, back edges go down. Computes dfi, 
		parent for nodes and type (back, tree) for edges.
		Returns a directed graph and the nodes in dfs order.
		Throws an exception if the minimum degree is <3."""
	G2 = nx.DiGraph()

	positions = []
	depth_first_index = dict()
	parent = dict()
	degrees = dict()
	num_seen = 0
	for (u,v,d) in dfs(G, source):
		if d=='tree':
			G2.add_edge(v,u, {'type':d}) #tree edges go up
			parent[v] = u
		elif not G2.has_edge(u,v): #we also see the edge to the parent here
			G2.add_edge(v,u, {'type':d}) #back edges go down
				
		for x in (u,v): #compute the dfs order
			if not x in depth_first_index:
				degrees[x] = 0
				depth_first_index[x] = num_seen
				num_seen +=1
				positions.append(x)
			degrees[x] += 1

				
	if num_seen!=len(G):
		raise ConnEx('disconnected')

	for (x,d) in degrees.iteritems():
		if d//2<3: raise ConnEx('min degree', G.edges(x))

	nx.set_node_attributes(G2,'dfi', depth_first_index)
	nx.set_node_attributes(G2,'parent', parent)
	nx.set_node_attributes(G2,'real', dict.fromkeys(G2.nodes_iter(), False))

	return G2, positions

def chain_decomposition(G, checker):
	""" Decomposes G into chains. The first three chains form a K23.
		Assigns a chain to every edge.
		Returns a list of chains."""

	source = (G.nodes_iter()).next()
	G, nodes_in_dfs_order = direct_and_tag(G, source)

	chains = find_k23(G, source, checker)

	chain_number = 3
	num = 0
	for x in nodes_in_dfs_order:
		num += 1
		#sorting is unnecessary for correctness, but makes things slightly faster
		#since shorter chains are easier to be added (less intervals...)
		#for u in sorted(G.successors(x), key=lambda v:G.node[v]['dfi'], reverse=True):
		for u in G.successors(x):
			if G[x][u]['type'] == 'tree': #also see the edge to the parent
				continue

			chain = [x]
			#up in the graph until the next edge is in a chain or we're at the root
			while u!=None and not 'chain' in G[chain[-1]][u]:
				G[chain[-1]][u]['chain'] = chain_number
				chain.append(u)
				u = G.node[u]['parent']
			
			if len(chain)==1:
				assert x == source
				#we get here when we encounter the chains of the k23
				continue

			start = chain[0]
			first_node = chain[1]
			last_node = chain[-1]
			parent = G[chain[-1]][u]['chain'] if u!=None else 0

			#classify the chain
			p = chains[parent]
			if start == p.start or p.num()==0 and start==p.end: 
				type = 2
			elif inner_node_of(G,start) == p.num():
				type = 1
			else:
				type = 3

			chains.append(Chain(
					G,
					start,
					first_node,
					last_node,
					parent,
					type,
					chains,
					checker))
			chain_number = chain_number + 1

	#for (u,v) in G.edges_iter():
	#	assert 'chain' in G[u][v], "this should be handled in the chain constructor"

	return G, chains

def find_k23(G, source, checker):
	"""Finds the initial K23 subdivision (and the first three chains)"""

	succ = G.successors(source) 
	#succ = sorted(G.successors(source), key = lambda x: G.node[x]['dfi'], reverse=True)
	cycle = set()
	cycle.add(source)
	cycle_list = []
	#find a basic cycle
	s = succ[0]
	while s!=source:
		cycle.add(s)
		cycle_list.append(s)
		s = G.node[s]['parent']

	#find a second chain
	for s in succ[1:]:
		t = s
		while not t in cycle:
			t = G.node[t]['parent']
		if not t == source:
			break

	if t==source:
		raise ConnEx("no k23", (source,cycle_list[0]), (source,cycle_list[-1]))

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
	C.append(Chain(G, chains[0][0], chains[0][1], chains[0][-1], None, None, None, checker))
	C.append(Chain(G, chains[1][0], chains[1][1], chains[1][-1], 0, 2, C, checker))
	C.append(Chain(G, chains[2][0], chains[2][1], chains[2][-1], 0, 2, C, checker))
	for i in xrange(3):
		C[i].add()

	return C
