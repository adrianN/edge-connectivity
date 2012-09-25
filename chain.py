from helper import *
from conn_exceptions import ConnEx

class Chain:
	""" A chain C. Stores s(C), t(C), the first edge, p(C), type(C) """
	def __init__(self, G, start, first_node, end, parent, type, chains, checker):
		self.start = start
		self.first_node = first_node
		self.end = end
		self.parent = chains[parent] if chains else None
		self.type = type
		self.type3 = []
		self.children = [[],[],[]]
		self.graph = G
		self.is_added = False
		self.checker = checker
		if parent != None: self.parent.add_child(self)
		if type == 3:
			c = inner_node_of(self.graph, start)
			if c==len(chains):
				raise ConnEx('cut edge',(start,G.node[start]['parent']))
			chain = chains[c]
			chain.add_type3(self)

	def num(self):
		return self.graph[self.start][self.first_node]['chain']

	def add_type3(self, chain):
		self.type3.append(chain)

	def add_child(self,chain):
		self.children[chain.type - 1].append(chain)

	def add(self):
		self.is_added = True
		self.graph.node[self.start]['real'] = True
		self.graph.node[self.end]['real'] = True
		self.checker.add(self.nodes())

	def nodes(self):
		G = self.graph
		yield self.start
		next = self.first_node
		last = self.end
		while next != last:
			yield next
			next = G.node[next]['parent']
		yield last 

	def __str__(self):
		return str((
			"start", self.start, 
			"fn", self.first_node, 
			"end", self.end, 
			"type", self.type, 
			"num", self.num(), 
			"parent", self.parent.num() if self.parent else None))

def is_addable(chain):
	"""Brute force check that a chain is addable. Do not use if you like linear time"""
	if chain.num() == 0: return True
	if chain.is_added: return False

	#only bad case: both endpoints not real and no real node between them
	G = chain.graph
	if G.node[chain.start]['real'] or G.node[chain.end]['real']:
		return True

	return any(map(lambda x: G.node[x]['real'], 
			tree_path_nodes(chain.graph, chain.end, chain.start)))



