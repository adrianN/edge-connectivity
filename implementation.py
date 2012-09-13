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

def direct_and_tag(G, source = None):
	""" Makes tree edges go up, back edges go down. Computes dfi, parent for nodes and type for edges"""
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

	return G2

def chain_decomposition(G, source = None):
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
				chains.append((chain[0], chain[1], chain[-1],G[chain[-1]][u]['chain']))
				chain_number = chain_number + 1

	check_chain_decomposition(G, chains)

	return G

def chain_edge_iter(G, chain):
	start, next, last, _ = chain
	assert G[start][next]

	yield start, next
	p = G.node[next]['parent']
	while next != last:
		yield next, p
		next = p
		p = G.node[p]['parent']

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

	return [(chains[0][0], chains[0][1], chains[0][-1], None), 
			(chains[1][0], chains[1][1], chains[1][-1], 0),
			(chains[2][0], chains[2][1], chains[2][-1], 0)]

def start(chain):
	return chain[0]
def end(chain):
	return chain[2]
def parent(chain):
	return chain[3]
def num(G, chain):
	return G[chain[0]][chain[1]]['chain']

def check_chain_decomposition(G, chains):
	for (u,v) in G.edges_iter():
		assert 'chain' in G[u][v]

	for (i,chain) in enumerate(chains):
		assert num(G,chain) == i, str(i) + '\t' + str(chain) + '\t' + str(num(G,chain))
		for u,v in chain_edge_iter(G, chain):
			assert G[u][v]['chain'] == i, str(chain) + '\n' + str(G[u][v]) + '\n' + str(i)


def check_basic_information(G):
	assert nx.is_directed(G), "G is not directed!"

	dfi = nx.get_node_attributes(G,'dfi')
	parent = nx.get_node_attributes(G,'parent')
	edge_type = nx.get_edge_attributes(G, 'type')

	for (u,v) in G.edges_iter():
		#print u,v, dfi[u], dfi[v], edge_type[u,v], parent[u], parent[v]
		assert u in dfi, "Not all nodes have a dfi! " + str(u)
		assert v in dfi, "Not all nodes have a dfi!" + str(v)
		assert (u,v) in edge_type
		assert edge_type[(u,v)] == 'back' and dfi[u]<dfi[v] or edge_type[(u,v)] == 'tree' and dfi[u]>dfi[v]
		assert not edge_type[(u,v)] == 'tree' or parent[u] == v

G = nx.complete_graph(4)
G2 = chain_decomposition(G)
check_basic_information(G2)