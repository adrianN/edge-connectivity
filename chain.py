from helper import *

class Chain:
	def __init__(self, G, start, first_node, end, parent, type, chains):
		self.start = start
		self.first_node = first_node
		self.end = end
		self.parent = chains[parent] if chains else None
		self.type = type
		self.type3 = []
		self.children = [[],[],[]]
		self.graph = G
		self.is_added = False
		if parent != None: self.parent.add_child(self)
		if type == 3:
			chain = chains[inner_node_of(self.graph, start)]
			chain.add_type3(self)

	def num(self):
		return self.graph[self.start][self.first_node]['chain']

	def add_type3(self, chain):
		self.type3.append(chain)

	def add_child(self,chain):
		self.children[chain.type - 1].append(chain)

	def add(self):
		"""Assert that a chain can be added and if yes, do so"""
		assert is_addable(self), "Can't add " + str(self)
		self.is_added = True
		self.graph.node[self.start]['real'] = True
		self.graph.node[self.end]['real'] = True
		print str(self), list(self.nodes())

	def edges(self):
		G = self.graph

		start = self.start
		next = self.first_node
		last = self.end
		assert G[start][next]

		yield start, next
		for e in tree_path_edges(G,next,last):
			yield e

	def nodes(self):
		for u,v in self.edges():
			yield u
		yield v

	def __str__(self):
		return str((
			"start", self.start, 
			"fn", self.first_node, 
			"end", self.end, 
			"type", self.type, 
			"num", self.num(), 
			"parent", self.parent.num() if self.parent else None))

def is_addable(chain):
	if chain.num() == 0: return True
	if chain.is_added: return False

	#only bad case: both endpoints not real and no real node between them
	G = chain.graph
	if G.node[chain.start]['real'] or G.node[chain.end]['real']:
		return True

	return any(map(lambda x: G.node[x]['real'], 
			tree_path_nodes(chain.graph, chain.end, chain.start)))



