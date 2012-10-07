import networkx as nx
from conn_exceptions import CertEx

class Checker:
	def __init__(self, G):
		self.orig = G
		self.paths = []

	def add(self, path):
		self.paths.append(path)

	def verify(self):
		""" checks that the certificate is valid """
		rebuild = nx.MultiGraph()
		for i,path in enumerate(self.paths):
			self.paths[i] = list(path)
			rebuild.add_path(self.paths[i])

		degrees = dict()
		for u,v in rebuild.edges_iter():
			if not self.orig.has_edge(u,v):
				raise CertEx("graphs not isomorphic")		
			try:
				degrees[u] += 1
			except KeyError: degrees[u] = 1
			try:
				degrees[v] += 1
			except KeyError: degrees[v] = 1

		if not all(degrees[x] >=3 for x in rebuild.nodes_iter()):
			raise CertEx("minimum degree")
		if not len(self.orig.edges()) == len(rebuild.edges()): 
			raise CertEx("graphs are not isomorphic")

		# remove paths in reverse order. the last path is always an edge in self.rebuild
		# hence it is easy to check whether it subdivides the same edge twice.
		while len(self.paths)>3:
			#assert all(degrees[u] == rebuild.degree(u) for u in rebuild.nodes_iter())	

			p = self.paths.pop()
			u,v = p[0],p[-1]
			assert u in rebuild
			assert v in rebuild
			for x in p[1:-1]:
				if x in rebuild: # the path is not an ear
					print x,'in the graph'
					raise CertEx('contains existing inner')

			if u==v:
				if not degrees[u]>=5: 
					raise CertEx("loop at nonreal")

			if not rebuild.has_edge(u,v): 
				print u,v
				raise CertEx("no edge ")
			
			if degrees[u] == degrees[v] == 2:
				#if u and v subdivide the same edge they have one endpoint of the edge
				#and either u or v as neighbor
				#we don't check len(neighbors) since having only two neighbors is perfectly
				#fine as long as there are multiple edges to them
				raise CertEx('divides same edge twice')
			
			rebuild.remove_edge(u,v)
			degrees[u] -= 1
			degrees[v] -= 1
			for x in (u,v):
				if degrees[x] == 2: 
					#replaces a degree 2 node by an edge 
					try:
						a,b = rebuild.neighbors(x)
					except ValueError:
						#double edge
						a = b = rebuild.neighbors(x)[0]
					rebuild.remove_node(x)
					rebuild.add_edge(a,b)


		if len(rebuild)!=2 or rebuild.number_of_edges()!=3:
			print len(G), len(G.edges())
			raise CertEx("graph not a k23 at the end")
		return True
