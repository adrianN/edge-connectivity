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

def add_chains(G, chains):
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
				else:
					print "can't add ",head
	
	def add_type3(chain):
			assert not chain.is_added
			assert chain.type == 3
			l = []
			c = chain
			print 'add with ancestors ', c
			while not c.is_added:
				l.append(c)
				c = c.parent
			if is_addable(l[-1]):
				while l:
					l.pop().add()

	for chain in chains:
		assert chain.is_added, "Chain " + str(chain) + " is not yet added"
		print 'Working on', chain

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



for i in range(100):
	print "===============",i,"==============="
	G = rg.make_simple(rg.random_3_edge_connected(10))
	G, chains = chain_decomposition(G)

	print to_dot(G)
	print '\n'.join(map(str,chains))
	print 
	check_chain_decomposition(G, chains)
	add_chains(G,chains)
