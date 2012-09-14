def tree_path_edges(G,u,v):
	p = u
	while p!=v:
		u = p
		p = G.node[p]['parent']
		yield u,p

def tree_path_nodes(G,u,v):
	for x,y in tree_path_edges(G,u,v):
		yield x
	
	yield v

def to_dot(G):
	s = ["digraph G {",'rankdir = BT']
	for u,v in G.edges():
		edge = '\t' + str(u) + "->" + str(v) + " [ "
		edge = edge + "label = \"" + str(G[u][v]['chain']) + '"'
		edge = edge + ", constraint = " + str(G[u][v]['type']=='tree') 
		edge = edge + ', weight = ' + ('100' if G[u][v]['type'] == 'tree' else '1') + "]"
		s.append(edge)
	s.append('}')
	return '\n'.join(s)
