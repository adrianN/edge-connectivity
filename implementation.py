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
		""" Computes an order and adds segments in that order """
		if segments == []: return
		order = order_segments(G, segments)
		for segment in order:
			for chain in segment.starters:
				assert not chain.is_added, "chain "+str(chain)+" is already added"
				add_type3(chain)
			if not segment.head.is_added:
				assert segment.starters == []
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
		while l:
			l.pop().add()

	for chain in chains:
		assert chain.is_added, "Chain " + str(chain) + " is not yet added"

		#all type 2 chains can be added, since chain.start is real
		for child in chain.children[1]:
			if not child.is_added: child.add()

		#every type one child gets its own segment. These are all segments that will
		#be created, we only add chains to them
		segments = map(Segment, chain.children[0])

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
	checker.verify()

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

def no(nodes, graphs):
	for i in xrange(graphs//3):
		print i
		G = rg.not_3_conn(nodes)
		G = rg.make_simple(G)
		yield G
	for i in xrange(graphs//3):
		print i+graphs//3
		G = rg.not_3_conn(nodes, 'dense')
		G = rg.make_simple(G)
		yield G
	for i in xrange(graphs//3):
		print i+2*graphs//3
		G = rg.not_3_conn(nodes, 'sparse')
		G = rg.make_simple(G)
		yield G
	print

def yes(nodes, graphs):
	for i in xrange(graphs//3):
		print i
		G = rg.make_simple(rg.random_3_edge_connected(nodes))
		yield G
	for i in xrange(graphs//3):
		print i+graphs//3
		G = rg.make_simple(rg.dense_3_edge_connected(nodes))
		yield G
	for i in xrange(graphs//3):
		print i+2*graphs//3
		G = rg.make_simple(rg.sparse_3_edge_connected(nodes))
		yield G
	print

def prepare_yes_no(nodes, graphs):
	print 'yes'
	y = list(yes(nodes,graphs))
	f = open('/Users/aneumann/Desktop/yes.g','w')
	cPickle.dump(y,f)
	f.close()
	print 'no'
	n = list(no(nodes,graphs))
	f = open('/Users/aneumann/Desktop/no.g','w')
	cPickle.dump(n,f)
	f.close()

def read_yes_no():
	f = open('/Users/aneumann/Desktop/yes.g','r')
	y = cPickle.load(f)
	f.close()
	f = open('/Users/aneumann/Desktop/no.g','r')
	n = cPickle.load(f)
	f.close()
	return y,n

y,n = read_yes_no()
n = []
# print 'down to business'
#cProfile.run('main(y, n)')
main(y,n)

#prepare_yes_no(5000,60)

#main(yes(200,12),no(200,12))
