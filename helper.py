class ComparableMixin:
  def __eq__(self, other):
    return not self<other and not other<self
  def __ne__(self, other):
    return not self == other
  def __gt__(self, other):
    return other<self
  def __ge__(self, other):
    return not self<other
  def __le__(self, other):
    return not other<self

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
	s = ["digraph G {"]
	def n(u):
		return '"' + str(G.node[u]['dfi']) + '"'
	for u,v in G.edges():
		if G.node[u]['dfi'] > G.node[v]['dfi']:
			u,v = v,u
		edge = '\t' + n(u) + "->" + n(v) + " [ "
		chain = G[u][v]['chain'] if 'chain' in G[u][v] else -1
		edge = edge + "label = \"" + str(chain) + '"'
		edge = edge + ", constraint = " + str(G[u][v]['type']=='tree') 
		edge = edge + ", color = " + ("red" if G[u][v]['type']=='back' else 'black')
		edge = edge + ', weight = ' + ('100' if G[u][v]['type'] == 'tree' else '1') + "]"
		s.append(edge)
	s.append('}')
	return '\n'.join(s)

def inner_node_of(G, node):
	try:
		p = G.node[node]['parent']
		return G[node][p]['chain']
	except KeyError:
		return None