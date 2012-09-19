import networkx as nx
import random_graph as rg
from chain_decomposition import *
from tests import *

def toStr(G):
	attr = nx.get_edge_attributes(G,'type')
	l = []
	for (u,v) in G.edges_iter():
		l.append(str(u)+'-'+str(v)+' '+str(attr[(u,v)]))
	return '\n'.join(l)

nx.Graph.__str__ = toStr

class Segment:
	def __init__(self, chain):
		self.head = chain
		self.starters = []
		self.attachment_points = [chain.start, chain.end]
		chain.segment = self

class Checker:
	def __init__(self, G):
		self.orig = G
		self.rebuild = nx.MultiGraph()
		self.paths = []

	def add(self, path):
		self.rebuild.add_path(path)
		self.paths.append(path)

	def verify(self):
		#TODO proper isomorphism check
		if not len(self.orig) == len(self.rebuild): return False
		if not len(self.orig.edges()) == len(self.rebuild.edges()): return False

		def smoothe(u):
			a,b = self.rebuild.neighbors(u)
			self.rebuild.remove_node(u)
			self.rebuild.add_edge(a,b)

		def remove_and_smoothe(u,v):
			self.rebuild.remove_edge(u,v)
			for x in (u,v):
				if self.rebuild.degree(x) == 2: smoothe(x)

		while len(self.paths)>3:
			p = self.paths.pop()
			u,v = p[0],p[-1]
			if not self.rebuild.has_edge(u,v): return False
			case = 0
			if self.rebuild.degree(v) > 3: case += 1
			if self.rebuild.degree(u) > 3: case += 1

			if case == 0: #u,v both subdivide an edge
				a,b = [x for x in self.rebuild.neighbors(u) if not x == v]
				c,d = [x for x in self.rebuild.neighbors(v) if not x == u]
				if len(set([a,b,c,d])) < 3: return False
			elif case == 1:
				pass # always okay
			elif case == 2:
				pass # always okay

			remove_and_smoothe(u,v)

		if len(G)!=2 or len(G.edges())!=3:
			return False

		
def make_segment(chain):
	chains = []
	segment = None
	source = chain
	while not chain.is_added:
		try:
			segment = chain.segment
			break
		except AttributeError:
			chains.append(chain)
			chain = chain.parent
	if not segment: return None
	
	segment.attachment_points.append(source.start)
	segment.starters.append(source)
	for c in chains: c.segment = segment
	return segment

def add_chains(G, chains, checker):
	def order_and_add(segments):
		added = 0
		added_something = True
		while added != len(segments):
			if not added_something: raise Exception("can't add all segments, "+str(added)+ " " + str(len(segments)))
			added_something = False
			for s in segments:
				head = s.head
				assert head.type == 1
				if is_addable(head):
					head.add()
					map(add_type3,s.starters)
					for v in s.attachment_points:
						assert G.node[v]['real']
					added_something = True
					added += 1
	
	def add_type3(chain):
			assert not chain.is_added
			assert chain.type == 3
			l = []
			c = chain
			while not c.is_added:
				l.append(c)
				c = c.parent
			if is_addable(l[-1]):
				while l:
					l.pop().add()

	for chain in chains:
		assert chain.is_added, "Chain " + str(chain) + " is not yet added"

		segments = []
		for c in chain.children[0]:
			segments.append(Segment(c))

		
		for c in chain.type3:
			segment = make_segment(c)
			if not segment:
				add_type3(c)


				#all type 2 chains can be added, since chain.start is real
		for child in chain.children[1]:
			if not child.is_added: child.add()

		order_and_add(segments)

		for c in chain.children[0] + chain.children[1] + chain.type3:
			assert c.is_added, "didn't add " +str(c)

def check_connectivity(G):
	checker = Checker(G)
	G, chains = chain_decomposition(G, checker)
	check_chain_decomposition(G,chains) # optional
	try:
		add_chains(G, chains, checker)
	except Exception as e:
		print e
		return False
	if not checker.verify():
		raise Exception('certificate invalid')
	return True

for i in range(1000):
	print "===============",i,"==============="
	G = rg.make_simple(rg.random_3_edge_connected(100))
	check_connectivity(G)
