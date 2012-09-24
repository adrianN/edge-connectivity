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

def order_intervals(intervals, start, target):
	G = nx.Graph()
	for i in intervals:
		G.add_node(i.data)

	def add_edge(i1, i2):
		G.add_edge(i1.data, i2.data)

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
				add_edge(i,i2)

		if stack and r>= stack[-1].endpoints[0]:
			add_edge(i,stack[-1])

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
				add_edge(i,i2)

		if stack and l<= stack[-1].endpoints[1]:
			add_edge(i,stack[-1])

		stack.append(i)

	order = list(nx.dfs_preorder_nodes(G,start))

	if not len(order) == len(G):
		seen = set(order)
		for v in G:
			if v in seen: continue
			raise IntervalException(list(nx.dfs_preorder_nodes(G,v)))
	return order

def order_segments(G, segments):
	def dfi(x):
		return G.node[x]['dfi']

	def cut_edges(highest, lowest):
		edge1 = (highest, G.node[highest]['parent'])
		assert nx.is_directed(G)
		c = inner_node_of(G,lowest)
		l = [v for v in G.predecessors(lowest) if G[v][lowest]['chain'] == c]
		assert len(l) == 1
		edge2 = (lowest, l[0])
		return edge1, edge2

	def extrema(segments):
		mins = [min(s.attachment_points, key = dfi) for s in segments]
		maxes = [max(s.attachment_points, key = dfi) for s in segments]
		highest = min(mins, key=dfi)
		lowest = max(maxes, key=dfi)
		return highest, lowest

	highest, lowest = extrema(segments)

	path = list(tree_path_nodes(G,lowest,highest))
	real_nodes = [x for x in path if G.node[x]['real']]	

	if not real_nodes:
		raise ConnEx('can\'t add all intervals, because there are no real nodes', 
			cut_edges(highest,lowest))

	positions = dict((x,i) for (i,x) in enumerate(path))
	pos = lambda x: positions[x]

	assert -1 not in path
	real_intervals = [Interval(-1,pos(x),'real_node') for x in real_nodes]

	segment_intervals = []
	for s in segments:

		a = sorted([pos(x) for x in s.attachment_points])

		for x in a[1:]:
			segment_intervals.append(Interval(a[0],x,s))
		for x in a[1:-1]:
			segment_intervals.append(Interval(x,a[-1],s))

	try:
		ordered_int = order_intervals(
			real_intervals+segment_intervals, 'real_node', len(segments))
	except IntervalException as l:
		raise ConnEx("can't add all intervals",
			cut_edges(*extrema(l.args[0])))

	# seen = set()
	# ordered_segments = []
	# for interval in ordered_int:
	# 	if interval.data != 'real_node' and not interval.data in seen:
	# 		seen.add(interval.data)
	# 		ordered_segments.append(interval.data)
	assert ordered_int[0] == 'real_node'
	return ordered_int[1:]
	# return ordered_segments

def make_interval(segment):
	pass