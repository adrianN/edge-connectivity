import networkx as nx
import random_graph as rg
from chain_decomposition import *
from tests import *
from conn_exceptions import *
import traceback as tb
from intervall_ordering import order_segments

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

	def __str__(self):
		return str(self.attachment_points)

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
		if not len(self.orig) == len(self.rebuild): 
			raise CertEx("different number of nodes")
		if not len(self.orig.edges()) == len(self.rebuild.edges()): 
			raise CertEx("different number of edges")

		def smoothe(u):
			assert self.rebuild.degree(u)==2
			try:
				a,b = self.rebuild.neighbors(u)
			except ValueError:
				#double edge
				a = b = self.rebuild.neighbors(u)[0]
			self.rebuild.remove_node(u)
			self.rebuild.add_edge(a,b)

		def remove_and_smoothe(u,v):
			self.rebuild.remove_edge(u,v)
			for x in (u,v):
				if self.rebuild.degree(x) == 2: smoothe(x)

		while len(self.paths)>3:
			p = self.paths.pop()
			u,v = p[0],p[-1]
			assert u in self.rebuild
			assert v in self.rebuild
			for x in p[1:-1]:
				if x in self.rebuild: 
					print x,'in the graph'
					raise CertEx('contains existing inner')

			if u==v:
				if not self.rebuild.degree(u)>=5: 
					raise CertEx("loop at nonreal")

			if not self.rebuild.has_edge(u,v): 
				print u,v
				raise CertEx("no edge ")
			
			if self.rebuild.degree(u) == self.rebuild.degree(v) == 2:
				raise CertEx('divides same edge twice')
			
			remove_and_smoothe(u,v)
			

		if len(self.rebuild)!=2 or len(self.rebuild.edges())!=3:
			print len(G), len(G.edges())
			raise CertEx("graph not a k23 at the end")
		return True
		
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
		if segments == []: return
		order = order_segments(G, segments)
		assert len(order) == len(segments)
		for segment in order:
			for chain in segment.starters:
				assert not chain.is_added, "chain "+str(chain)+" is already added"
				add_type3(chain)
			if not segment.head.is_added:
				segment.head.add()
			
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

		#all type 2 chains can be added, since chain.start is real
		for child in chain.children[1]:
			if not child.is_added: child.add()

		segments = []
		for c in chain.children[0]:
			segments.append(Segment(c))

		
		for c in chain.type3:
			segment = make_segment(c)
			if not segment:
				add_type3(c)

		order_and_add(segments)


def check_connectivity(G):
	checker = Checker(G)
	try:
		G, chains = chain_decomposition(G, checker)
		check_chain_decomposition(G,chains) # optional
		add_chains(G, chains, checker)
	except ConnEx as e:
		print type(e), e.args
		return False
	checker.verify()

	return True

for i in range(1000):
	print "===============",i,"==============="
	G = rg.make_simple(rg.random_3_edge_connected(10))

	assert naive_connectivity(G) ==  check_connectivity(G)


p = 0.04
for i in range(1000):
	print "===============",i,"==============="
	n = 20
	G = nx.fast_gnp_random_graph(n,p)
	print p, p*n*(n-1)/2
	try:
		if check_connectivity(G):
			p *= 0.99
			assert naive_connectivity(G)
		else:
			p *= 1.01
			assert not naive_connectivity(G)
	except:
		print list(nx.generate_adjlist(G))