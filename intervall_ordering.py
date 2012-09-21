import networkx as nx
from conn_exceptions import ConnEx
from helper import tree_path_nodes

class Interval:
	def __init__(self, left, right, data):
		self.endpoints = (left,right)
		self.data = data


def order_intervals(intervals, start):
	assert start in intervals
	G = nx.DiGraph()
	for d in set([i.data for i in intervals]):
		G.add_node(d)

	#right to left sweep according to left endpoints
	#linear time with proper sorting
	stack = []
	for i in sorted(intervals, reverse = True, key = lambda i: i.endpoints[0]):
		l, r = i.endpoints
		while stack and r>stack[-1].endpoints[1]:
			stack.pop()
		if stack and r>= stack[-1][0]:
			G.add_edge(i,stack[-1])
		stack.append(i)

	#left to right sweep according to right endpoints
	stack = []
	for i in sorted(intervals, reverse = True, key = lambda i: i.endpoints[1]):
		l, r = i.endpoints
		while stack and l<stack[-1].endpoints[0]:
			stack.pop()
		if stack and l<= stack[-1][1]:
			G.add_edge(i,stack[-1])
		stack.append(i)

	order = list(nx.dfs_preorder_nodes(G,start))
	if len(order) != len(intervals):
		seen = set(order)
		for interval in intervals:
			if not interval in seen: break
		#todo compute cut
		raise ConnEx("can't add all intervals")

	return order

def order_segments(G, segments):
	f = lambda c : c(( c(s.attachment_points, key=lambda p: G.node[p]['dfi']) ) for s in segments)
	highest = f(min)
	lowest = f(max)
	path = tree_path_nodes(G,lowest,highest)

	flip = lambda (x,y): (y,x)
	positions = dict(map(flip, enumerate(path)))

	real_nodes = [(pos, x) for (pos, x) in enumerate(path) if G.node[x]['real']]	
	real_intervals = [Interval(-1,pos,None) for (pos,_) in real_nodes]

	segment_intervals = []
	for s in segments:
		a = sorted(s.attachment_points)
		for x in a[1:]:
			segment_intervals.append(Interval(a[0],x,s))
		for x in a[1:-1]:
			segment_intervals.append(Interval(x,a[-1],s))

	ordered_int = order_intervals(real_intervals+segment_intervals, real_intervals[0])
	seen = set()
	ordered_segments = []
	for interval in ordered_int:
		if interval.data != None and not interval in seen:
			seen.add(interval)
			ordered_segments.append(interval.data)
	return ordered_intervals 

def make_interval(segment):
	pass