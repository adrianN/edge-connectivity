import networkx as nx
import random_graph as rg
from tests import *
from chain import *
from helper import *
from chain_decomposition import *

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
				print [c for c in chains if not c.is_added]
				raise Exception("can't add all chains of type 1")

	for chain in chains:
		assert chain.is_added
		#all type 2 chains can be added, since chain.start is real
		for child in chain.children2:
			if not child.is_added: child.add()

		#Chains from type3 can be added because child.start is above chain.end
		for child in chain.type3:
			if child.is_added:
				print "this shouldn't happen"
				continue
			l = []
			c = child
			while not c.is_added:
				l.append(c)
				c = c.parent
			while l:
				l.pop().add()

		order_and_add(chain.children1)



G = rg.make_simple(rg.random_3_edge_connected(10))
G, chains = chain_decomposition(G)
check_chain_decomposition(G, chains)
add_chains(G,chains)