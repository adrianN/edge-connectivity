import networkx as nx
from conn_exceptions import CertEx

class Checker:
	def __init__(self, G):
		self.orig = G
		self.paths = []

	def add(self, path):
		self.paths.append(path)

	def verify(self):
		rebuild = nx.MultiGraph()
		for path in self.paths:
			rebuild.add_path(path)
		#TODO proper isomorphism check
		if not len(self.orig) == len(rebuild): 
			raise CertEx("different number of nodes")
		if not len(self.orig.edges()) == len(rebuild.edges()): 
			raise CertEx("different number of edges")

		def smoothe(u):
			assert rebuild.degree(u)==2
			try:
				a,b = rebuild.neighbors(u)
			except ValueError:
				#double edge
				a = b = rebuild.neighbors(u)[0]
			rebuild.remove_node(u)
			rebuild.add_edge(a,b)

		def remove_and_smoothe(u,v):
			rebuild.remove_edge(u,v)
			for x in (u,v):
				if rebuild.degree(x) == 2: smoothe(x)

		while len(self.paths)>3:
			p = self.paths.pop()
			u,v = p[0],p[-1]
			assert u in rebuild
			assert v in rebuild
			for x in p[1:-1]:
				if x in rebuild: 
					print x,'in the graph'
					raise CertEx('contains existing inner')

			if u==v:
				if not rebuild.degree(u)>=5: 
					raise CertEx("loop at nonreal")

			if not rebuild.has_edge(u,v): 
				print u,v
				raise CertEx("no edge ")
			
			if rebuild.degree(u) == rebuild.degree(v) == 2:
				raise CertEx('divides same edge twice')
			
			remove_and_smoothe(u,v)
			

		if len(rebuild)!=2 or len(rebuild.edges())!=3:
			print len(G), len(G.edges())
			raise CertEx("graph not a k23 at the end")
		return True
