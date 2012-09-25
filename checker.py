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

		for e in self.orig.edges_iter():
			if not rebuild.has_edge(*e):
				raise CertEx("graphs not isomorphic")		
		if not len(self.orig.edges()) == len(rebuild.edges()): 
			raise CertEx("graphs are not isomorphic")

		def smoothe(u):
			""" replaces a degree 2 node by an edge """
			assert rebuild.degree(u)==2
			try:
				a,b = rebuild.neighbors(u)
			except ValueError:
				#double edge
				a = b = rebuild.neighbors(u)[0]
			rebuild.remove_node(u)
			rebuild.add_edge(a,b)

		def remove_and_smoothe(u,v):
			""" removes an edges, smoothes the endpoints """
			rebuild.remove_edge(u,v)
			for x in (u,v):
				if rebuild.degree(x) == 2: smoothe(x)

		# remove paths in reverse order. the last path is always an edge in self.rebuild
		# hence it is easy to check whether it subdivides the same edge twice.
		while len(self.paths)>3:
			p = self.paths.pop()
			u,v = p[0],p[-1]
			assert u in rebuild
			assert v in rebuild
			for x in p[1:-1]:
				if x in rebuild: # the path is not an ear
					print x,'in the graph'
					raise CertEx('contains existing inner')

			if u==v:
				if not rebuild.degree(u)>=5: 
					raise CertEx("loop at nonreal")

			if not rebuild.has_edge(u,v): 
				print u,v
				raise CertEx("no edge ")
			
			if rebuild.degree(u) == rebuild.degree(v) == 2:
				#if u and v subdivide the same edge they have one endpoint of the edge
				#and either u or v as neighbor
				#we don't check len(neighbors) since having only two neighbors is perfectly
				#fine as long as there are multiple edges to them
				raise CertEx('divides same edge twice')
			
			remove_and_smoothe(u,v)
			

		if len(rebuild)!=2 or len(rebuild.edges())!=3:
			print len(G), len(G.edges())
			raise CertEx("graph not a k23 at the end")
		return True
