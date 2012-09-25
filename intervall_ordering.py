import networkx as nx
from conn_exceptions import ConnEx
from helper import tree_path_nodes, inner_node_of

class Interval:
	def __init__(self, left, right, data):
		self.endpoints = (left,right)
		self.data = data


	def __str__(self):
		return ','.join([str(self.endpoints), str(self.data)])
		return str(self.endpoints)

class IntervalException(Exception): pass

def order_intervals(intervals, start):
	""" computes the intersection graph of the intervals, takes the data attribute
		of the intervals as nodes, hence intervals belonging to the same segment
		correspond to one node in the graph.
		returns a traversal starting from start. """
	G = nx.Graph()
	G.add_nodes_from((i.data for i in intervals))

	#right to left sweep according to left endpoints
	#linear time with proper sorting
	stack = []
	for i in sorted(intervals, reverse = True, key = lambda i: (i.endpoints[0], -i.endpoints[1])):
		special_connect = False
		l, r = i.endpoints

		while stack and r>stack[-1].endpoints[1]:
			i2 = stack.pop()
			#Since now the intervals don't pierce each other anymore,
			#we need to add this special edge
			if not special_connect and i2.endpoints[0] == l:
				special_connect = True
				G.add_edge(i.data,i2.data) 

		if stack and r>= stack[-1].endpoints[0]:
			G.add_edge(i.data, stack[-1].data) 

		stack.append(i)

	#left to right sweep according to right endpoints
	stack = []
	for i in sorted(intervals, key = lambda i: (i.endpoints[1], -i.endpoints[0])):
		l, r = i.endpoints
		special_connect = False

		while stack and l<stack[-1].endpoints[0]:
			i2 = stack.pop()
			if not special_connect and i2.endpoints[1] == r:
				special_connect = True
				G.add_edge(i.data, i2.data) 

		if stack and l<= stack[-1].endpoints[1]:
			G.add_edge(i.data, stack[-1].data)

		stack.append(i)

	order = list(nx.dfs_preorder_nodes(G,start))

	if not len(order) == len(G):
		seen = set(order)
		for v in G:
			if v in seen: continue
			raise IntervalException(list(nx.dfs_preorder_nodes(G,v)))
	return order

def order_segments(G, segments):
	""" Computes an order on the segments such that they can be added in that order.
		Throws a separation pair if no such order can be found. """

	def dfi(x):
		return G.node[x]['dfi']

	def cut_edges(highest, lowest):
		""" Computes the edges separating the two extremal attachment points
			of the segments """
		edge1 = (highest, G.node[highest]['parent'])
		c = inner_node_of(G,lowest)
		l = [v for v in G.predecessors(lowest) if G[v][lowest]['chain'] == c]
		assert len(l) == 1
		edge2 = (lowest, l[0])
		return edge1, edge2

	def extrema(segments):
		""" Computes the extremal attachment points for a bunch of segments"""
		mins = (min(s.attachment_points, key = dfi) for s in segments)
		maxes = (max(s.attachment_points, key = dfi) for s in segments)
		highest = min(mins, key=dfi)
		lowest = max(maxes, key=dfi)
		return highest, lowest

	#compute the dependent path and the real nodes on the path
	highest, lowest = extrema(segments)

	path = list(tree_path_nodes(G,lowest,highest))
	real_nodes = [x for x in path if G.node[x]['real']]	

	if not real_nodes:
		raise ConnEx('can\'t add all intervals, because there are no real nodes', 
			cut_edges(highest,lowest))

	positions = dict((x,i) for (i,x) in enumerate(path))

	#generate intervals for real nodes and segments
	assert -1 not in path
	intervals = [Interval(-1,positions[x],'real_node') for x in real_nodes]

	for s in segments:
		a = sorted([positions[x] for x in s.attachment_points])
		for x in a[1:]:
			intervals.append(Interval(a[0],x,s))
		for x in a[1:-1]:
			intervals.append(Interval(x,a[-1],s))

	#compute an order
	try:
		ordered_int = order_intervals(intervals, 'real_node')
	except IntervalException as l:
		raise ConnEx("can't add all intervals",
			cut_edges(*extrema(l.args[0])))

	assert ordered_int[0] == 'real_node'
	return ordered_int[1:]

def make_interval(segment):
	pass