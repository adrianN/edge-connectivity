import networkx as nx
import cProfile
import cPickle
import random_graph as rg
from implementation import check_connectivity
from helper import to_dot


def check_basic_information(G):
	assert nx.is_directed(G), "G is not directed!"

	dfi = nx.get_node_attributes(G,'dfi')
	parent = nx.get_node_attributes(G,'parent')
	edge_type = nx.get_edge_attributes(G, 'type')

	for (u,v) in G.edges_iter():
		#print u,v, dfi[u], dfi[v], edge_type[u,v], parent[u], parent[v]
		assert u in dfi, "Not all nodes have a dfi! " + str(u)
		assert v in dfi, "Not all nodes have a dfi!" + str(v)
		assert (u,v) in edge_type
		assert edge_type[(u,v)] == 'back' and dfi[u]<dfi[v] or edge_type[(u,v)] == 'tree' and dfi[u]>dfi[v]
		assert not edge_type[(u,v)] == 'tree' or parent[u] == v

def check_chain_decomposition(G, chains):
	for (u,v) in G.edges_iter():
		assert 'chain' in G[u][v]

	for (i,chain) in enumerate(chains):
		assert chain.num() == i, str(i) + '\t' + str(chain) + '\t' + str(chain.num())
		for u,v in chain.edges():
			assert G[u][v]['chain'] == i, str(chain) + '\n' + str(G[u][v]) + '\n' + str(i)

def naive_connectivity(G):
	if not nx.is_connected(G):
		print 'not connected!'
		return False
	for e in G.edges():
		for e2 in G.edges():
			G.remove_edge(*e)
			if not e==e2:
				G.remove_edge(*e2)
			if not nx.is_connected(G):
				print e,e2,'disconnect the graph'
				G.add_edge(*e)
				if not e==e2: G.add_edge(*e2)
				return False
			G.add_edge(*e)
			if not e==e2: G.add_edge(*e2)
	return True

def main(yes,no):
	print 'no'
	try:
		for i,G in enumerate(no):
			print i
			assert not check_connectivity(G)
		print 'yes'
		for i,G in enumerate(yes):
			print i
			assert check_connectivity(G)
	except AssertionError as e:
		print e
		print to_dot(G)

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

#y,n = read_yes_no()
#n = []
# print 'down to business'
#cProfile.run('main(y, n)', 'fooprof')
#main(y,n)

#prepare_yes_no(5000,60)

main(yes(10,20000),no(10,20000))