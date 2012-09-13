import networkx as nx

def toStr(G):
	attr = nx.get_edge_attributes(G,'type')
	l = []
	for (u,v) in G.edges_iter():
		l.append(str(u)+'-'+str(v)+' '+str(attr[(u,v)]))
	return '\n'.join(l)

nx.Graph.__str__ = toStr

def dfs(G,source=None):
	"""Produce edges in a depth-first-search starting at source."""
	# Based on http://www.ics.uci.edu/~eppstein/PADS/DFS.py
	# by D. Eppstein, July 2004.
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

def chain_decomposition(G):
	G2 = nx.DiGraph()
	G2.add_nodes_from(G.nodes_iter())
	positions = []
	seen = set()
	parent = dict((u,None) for u in G.nodes_iter())
	for (u,v,d) in dfs(G):
		if d=='tree':
			G2.add_edge(u,v, type=d)
			parent[u] = v
		else:
			if parent[v] != u:
				G2.add_edge(u,v, type=d)

		for x in (u,v):
			if not x in seen:
				seen.add(x)
				positions.append(x)

	seen = set()
	depth_first_index = dict(enumerate(positions))
	nx.set_node_attributes(G,'dfi',depth_first_index)
	nx.set_node_attributes(G,'parent',parent)

	return G2

G = nx.complete_graph(4)
print chain_decomposition(G)