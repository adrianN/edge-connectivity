import networkx as nx
from chain import *
from conn_exceptions import ConnEx

def successors(G,v):
	dfi = G.node[v]['dfi']
	return (x for x,data in G[v].iteritems() if G.node[x]['dfi']>dfi and data['type'] == 'back')

def dfs(G,source=None):
	"""Produce edges in a depth-first-search starting at source. 
	Edges are tagged as either 'tree' or 'back'"""
	# Very slight modification of the DFS procedure from networkx
	# One could unify this with compute_information, but it seemed cleaner this way
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


def compute_information(G, source = None):
	""" Computes dfi, parent for nodes and type (back, tree) for edges.
		Returns the nodes in dfs order.
		Throws an exception if the minimum degree is <3 or the graph is disconnected"""
	positions = []
	degrees = dict()
	num_seen = 0
	G.node[source]['parent'] = None
	for (u,v,d) in dfs(G, source):
		if d=='tree':
			G[v][u]['type'] = d
			G.node[v]['parent'] = u
		elif not 'type' in G[v][u]: #we also see the edge to the parent here
			G[v][u]['type'] = d
				
		for x in (u,v): #compute the dfs order
			if not 'dfi' in G.node[x]:
				degrees[x] = 0
				G.node[x]['dfi'] = num_seen
				G.node[x]['real'] = False
				num_seen +=1
				positions.append(x)
			degrees[x] += 1

				
	if num_seen!=len(G):
		raise ConnEx('disconnected')

	for (x,d) in degrees.iteritems():
		if d<6: raise ConnEx('min degree', G.edges(x))

	return positions

def chain_decomposition(G, checker):
	""" Decomposes G into chains. The first three chains form a K23.
		Assigns a chain to every edge.
		Returns a list of chains."""

	source = (G.nodes_iter()).next()
	nodes_in_dfs_order = compute_information(G, source)

	chains = find_k23(G, source, checker)

	chain_number = 3
	for x in nodes_in_dfs_order:
		#sorting is unnecessary for correctness, but makes things slightly faster
		#since shorter chains are easier to be added (less intervals...)
		#for u in sorted(G.successors(x), key=lambda v:G.node[v]['dfi'], reverse=True):
		for u in successors(G,x):
			start = x
			first_node = u
			if 'chain' in G[start][first_node]:
				assert start==source
				#we get here when we encounter the chains of the k23
				continue

			last_node = x

			while not (u is None or 'chain' in G[last_node][u]):
				G[last_node][u]['chain'] = chain_number
				last_node = u
				u = G.node[u]['parent']

			parent = G[last_node][u]['chain'] if u is not None else 0
			#classify the chain
			p = chains[parent]
			if start == p.start or parent==0 and start==p.end: 
				type = 2
			elif inner_node_of(G,start) == parent:
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

	succ = list(successors(G,source))
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
