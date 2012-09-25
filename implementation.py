import networkx as nx
import random_graph as rg
from chain_decomposition import *
from tests import *
from conn_exceptions import *
import traceback as tb
from intervall_ordering import order_segments
from checker import Checker
import cProfile
import cPickle

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
		"""Adds a type3 chain and all its ancestors (ancestors first)"""
		assert not chain.is_added
		assert chain.type == 3
		l = []
		c = chain
		while not c.is_added:
			l.append(c)
			c = c.parent
		#if is_addable(l[-1]):
		while l:
			l.pop().add()

	for chain in chains:
		assert chain.is_added, "Chain " + str(chain) + " is not yet added"

		#all type 2 chains can be added, since chain.start is real
		for child in chain.children[1]:
			if not child.is_added: child.add()

		#every type one child gets its own segment. These are all segments that will
		#be created, we only add chains to them
		segments = []
		for c in chain.children[0]: 
			segments.append(Segment(c))

		#for each type3 chain we walk upwards in the chain tree until we 
		#reach a chain that is already in a segment or is already added
		#if we encounter no chain that is on a segment, we can add this path 
		#in the chain tree, since t(chain) is already real (really? TODO)
		for c in chain.type3:
			segment = make_segment(c)
			if not segment:
				add_type3(c)

		#Lastly compute a proper order on the segments and add them.
		order_and_add(segments)


def check_connectivity(G):
	checker = Checker(G)
	try:
		G, chains = chain_decomposition(G, checker)
		add_chains(G, chains, checker)
	except ConnEx as e:
	 	print type(e), e.args
	 	return False
	#checker.verify()

	return True

def main(yes,no):
	print 'no'
	for i,G in enumerate(no):
		print i
		assert not check_connectivity(G)
	print 'yes'
	for i,G in enumerate(yes):
		print i
		assert check_connectivity(G)

def no():
	for i in xrange(10):
		G = rg.not_3_conn(1000)
		G = rg.make_simple(G)
		yield G

def yes():
	for i in xrange(10):
		G = rg.make_simple(rg.random_3_edge_connected(1000))
		yield G


f = open('/Users/aneumann/Desktop/yes.g','r')
y = cPickle.load(f)
f.close()
f = open('/Users/aneumann/Desktop/no.g','r')
n = cPickle.load(f)
f.close()
print 'down to business'
cProfile.run('main(y, n)')
#main(yes(),no())
