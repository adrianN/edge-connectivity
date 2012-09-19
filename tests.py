import networkx as nx

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
	for e in G.edges():
		for e2 in G.edges():
			G.remove_edge(*e)
			G.remove_edge(*e2)
			if not nx.is_connected(G):
				return False
			G.add_edge(*e)
			G.add_edge(*e)
	return True