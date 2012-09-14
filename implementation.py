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


def add_chains(G, chains):
	def order_and_add(chains):
		#todo linear time
		added = 0
		chains = [c for c in chains if not c.is_added]
		while added < len(chains):
			old_added = added
			for chain in chains:
				if is_addable(chain):
					chain.add()
					added += 1
			if added==old_added:
				raise Exception("can't add all chains of type 1 " + str([str(c) for c in chains if  not c.is_added]))

	def add_type3(chains):
		for child in chains:
			if child.is_added: #this might be the second run and we already have added some
				continue
			l = []
			c = child
			print 'add with ancestors ', c
			while not c.is_added:
				l.append(c)
				c = c.parent
			if is_addable(l[-1]):
				while l:
					l.pop().add()

	for chain in chains:
		assert chain.is_added
		#all type 2 chains can be added, since chain.start is real
		for child in chain.children2:
			if not child.is_added: child.add()

		#Chains from type3 can be added with their ancestors because child.start is above chain.end
		add_type3(chain.type3)

		order_and_add(chain.children1)

		add_type3(chain.type3)


for i in range(100):
	print "===============",i,"==============="
	G = rg.make_simple(rg.random_3_edge_connected(100))
	G, chains = chain_decomposition(G)

	print to_dot(G)
	print '\n'.join(map(str,chains))
	print 
	check_chain_decomposition(G, chains)
	add_chains(G,chains)
