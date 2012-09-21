import networkx as nx
from conn_exceptions import ConnEx
from helper import tree_path_nodes

class Interval:
	def __init__(self, left, right, data):
		self.endpoints = (left,right)
		self.data = data


	def __str__(self):
		return ','.join([str(self.endpoints), str(self.data)])
		return str(self.endpoints)

def order_intervals(intervals, start, target):
	G = nx.Graph()
	for i in intervals:
		G.add_node(i)

	def add_edge(i1, i2):
		G.add_edge(i1.data, i2.data)

	#right to left sweep according to left endpoints
	#linear time with proper sorting
	print 'right to left sweep', map(str,sorted(intervals, reverse = True, key = lambda i: (i.endpoints[0], -i.endpoints[1])))
	stack = []
	for i in sorted(intervals, reverse = True, key = lambda i: (i.endpoints[0], -i.endpoints[1])):
		special_connect = False
		l, r = i.endpoints
		print 'considering', i, 'stack', map(str,stack)
		while stack and r>stack[-1].endpoints[1]:
			i2 = stack.pop()
			if not special_connect and i2.endpoints[0] == l:
				special_connect = True
				add_edge(i,i2)
				print 'special connect', i, i2
			print i2
		if stack and r>= stack[-1].endpoints[0]:
			add_edge(i,stack[-1])
			print '\tconnect', i, stack[-1]
		stack.append(i)

	#left to right sweep according to right endpoints
	print 'left to right sweep', map(str,sorted(intervals, key = lambda i: (i.endpoints[1], -i.endpoints[0])))
	stack = []
	for i in sorted(intervals, key = lambda i: (i.endpoints[1], -i.endpoints[0])):
		l, r = i.endpoints
		special_connect = False
		print 'considering', i, 'stack', map(str,stack)
		while stack and l<stack[-1].endpoints[0]:
			i2 = stack.pop()
			if not special_connect and i2.endpoints[1] == r:
				special_connect = True
				add_edge(i,i2)
				print 'special connect', i, i2
			print i2
		if stack and l<= stack[-1].endpoints[1]:
			add_edge(i,stack[-1])
			print '\tconnect', i, stack[-1]
		stack.append(i)

	order = list(nx.dfs_preorder_nodes(G,start))
	print 'G:'
	print '\n'.join(map(lambda x:str(map(str,x)),G.edges()))
	print 'connected?', nx.is_connected(G)
	print 'order found', map(str, order)

	return order

def order_segments(G, segments):
	def dfi(x):
		return G.node[x]['dfi']
	mins = [min(s.attachment_points, key = dfi) for s in segments]
	maxes = [max(s.attachment_points, key = dfi) for s in segments]
	highest = min(mins, key=dfi)
	lowest = max(maxes, key=dfi)

	path = list(tree_path_nodes(G,lowest,highest))
	real_nodes = [x for x in path if G.node[x]['real']]	
	positions = dict((x,i) for (i,x) in enumerate(path))
	pos = lambda x: positions[x]
	print map(pos,mins), map(pos,maxes), pos(highest), pos(lowest), 'path', map(pos,path), map(pos,real_nodes)
	print mins, maxes, highest, lowest, 'path', path, real_nodes

	assert -1 not in path
	real_intervals = [Interval(-1,pos(x),'real_node') for x in real_nodes]

	segment_intervals = []
	for s in segments:
		print s,
		a = sorted([pos(x) for x in s.attachment_points])
		print a
		for x in a[1:]:
			segment_intervals.append(Interval(a[0],x,s))
		for x in a[1:-1]:
			segment_intervals.append(Interval(x,a[-1],s))

	ordered_int = order_intervals(real_intervals+segment_intervals, 'real_node', len(segments))
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