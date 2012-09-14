class Chain:
	def __init__(self, G, start, first_node, end, parent, type, chains):
		self.start = start
		self.first_node = first_node
		self.end = end
		self.parent = chains[parent] if chains else None
		self.type = type
		self.type3 = []
		self.children1 = []
		self.children2 = []
		self.graph = G
		self.is_added = False
		if type == 1:
			self.parent.add_child1(self)
		elif type == 2:
			self.parent.add_child2(self)
		elif type == 3:
			chain = chains[inner_node_of(self.graph, start)]
			chain.add_type3(self)

	def num(self):
		return self.graph[self.start][self.first_node]['chain']

	def add_type3(self, chain):
		self.type3.append(chain)

	def add_child1(self, chain):
		self.children1.append(chain)

	def add_child2(self, chain):
		self.children2.append(chain)

	def add(self):
		self.is_added = True
		self.graph.node[self.start]['real'] = True
		self.graph.node[self.end]['real'] = True

	def edges(self):
		G = self.graph

		start = self.start
		next = self.first_node
		last = self.end
		assert G[start][next]

		yield start, next
		p = G.node[next]['parent']
		while next != last:
			yield next, p
			next = p
			p = G.node[p]['parent']

	def __str__(self):
		return str((self.start, self.first_node, self.end, self.type))


def inner_node_of(G, node):
	try:
		p = G.node[node]['parent']
		return G[node][p]['chain']
	except KeyError:
		return None
