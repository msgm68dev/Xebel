#Source: https://www.geeksforgeeks.org/find-paths-given-source-destination/

# Python program to print all paths from a source to destination. 

from collections import defaultdict 
import time #For measuring codes execution time
import copy #for full clone of a list
from collections import Counter #For counting distinct values in list
import sys, os #for seeing Error line no.

from utils import *

DefaultParams = '1.0-999'
infty=float('inf')

class ijPaths:
	src = -1
	dst = -1
	def __init__(self, paths, epaths = None):
		if paths:
			self.Paths = sorted(paths, key=len)
			self.VLengths = [len(path) for path in paths]
			self.PathsNo = len(paths)
			if self.VLengths[0] > 0:
				self.src = paths[0][0]
				self.dst = paths[0][-1]
			else:
				raise Exception('First path\'s length is zero')
			if not epaths:
				self.EPaths = self._paths_to_epaths(paths)
			else:
				self.EPaths = epaths
			self.ELengths = [len(epath) for epath in self.EPaths]
		else:
			raise Exception('Error: NULL path')
			
	def _path_to_epath(self, path, ndigit = 0):
		if ndigit < 1:
			return [ str(path[i]) + '-' + str(path[i+1]) for i in range(len(path)-1)] 
		else:
			return [ str(path[i]).zfill(ndigit) + '-' + str(path[i+1]).zfill(ndigit) for i in range(len(path)-1)] 
	def _paths_to_epaths(self, paths, ndigit = 0):
		return [self._path_to_epath(path, ndigit) for path in paths]

	def _epath_similarity(self, ep1, ep2):
		shorter = ep1
		longer = ep2
		if len(ep1) > len(ep2):
			shorter = ep2
			longer = ep1
		counter = 0
		for edge in shorter:
			if edge in longer:
				counter = counter + 1
		return 1.0 * counter / len(shorter) 
	def _have_similar_epath_in_list(self, epath, epaths, acep):
			for ep in epaths:
				if self._epath_similarity(ep, epath) > acep:
					return True
			return False
	def prone(self, acep, aps):
		if acep <= 0 or aps <= 0:
			raise Exception('Acep & Aps are not set!')
		shortest_len = len(self.EPaths[0])
		pronned_paths = []
		pronned_epaths = []
		for i in range(self.PathsNo):
			ep = self.EPaths[i]
			if not self._have_similar_epath_in_list(ep, pronned_epaths, acep):
				if len(ep) <= aps * shortest_len:
					pronned_epaths.append(ep)
					pronned_paths.append(self.Paths[i])
		return ijPaths(pronned_paths, pronned_epaths)

	def print_stats(self, acep, aps):
		if self.VLengths[0] == 0:
			print('No path exist!')
			return
		elif self.ELengths[0] == 0:
			print('Just 1 path exist from', self.src, 'to', self.dst)
			return
		elif '-' not in self.EPaths[0][0]:
			raise Exception ('Epaths[0][0] is an Invalid path')
		lens_sum = dict(Counter(self.ELengths))
		print(" %d>%d ::  ce %.2f  ps %d \n# of paths: %d" % ( self.src , self.dst , round(acep, 2), aps, self.PathsNo))
		print(lens_sum)
		print(".")
	
	def Print(self):
		for p in self.Paths:
			print(p)
		print(".")

#This class represents a directed graph 
# using adjacency list representation 
class Graph: 
	# self.allPaths = [ [ [] for i in range(self.V) ] for i in range(self.V) ]
	# self.allpLengs = copy.deepcopy(self.allPaths)
	# self.paramdict = {'99-99.0': [ [ None for i in range(self.V) ] for i in range(self.V) ] }

	'''
	*   A dictionary with:
		+	Key: string of format: 'acep%:aps*', e.g. '80:3.5' 
		+	Value: list of lists (V * V list) of pronned paths from a source to a destination
		+	Example:	The value of _PATHs['80:3.5'][i][j] means: 
						List of paths from i to j regarding acep=80% and aps=3.5x
				The content is:
				$	an ijPaths instance with src=i, dst=j, acep=80, aps=3.5
				$	None (default): if we do not calculate paths i to 
					j with '80-3.5' but this key exist
	'''
	_PATHs = {}
	def __init__(self,dataset): 
			self.dataset = dataset
			tbl = file_to_table(dataset)
			array = [[int(x) for x in record] for record in tbl]
			self.topology = dataset.split('/')[-1].split('\\')[-1].split('.')[0]
  
			# default dictionary to store graph 
			self.graph = defaultdict(list) 
			
			#No. of vertices 
			self.V = max(max(e[0], e[1]) for e in array) + 1

			#Matrix representation 
			# M[i, j] = Weight		if specified in the dataset file (3rd column) 
			#			1			if not specified
			#			infty		if edge not exist!
			self.M = [[infty] * self.V]* self.V

			nEdge = 0
			for e in array:
				self._addEdge(e[0], e[1])
				nEdge += 1
				self.M[e[0]][e[1]] = e[2] if len(e) > 2 else 1
			
			#No. of Edges
			self.E = nEdge

			self._PATHs[DefaultParams] = [ [ None for i in range(self.V) ] for i in range(self.V) ]
			self.sync = False #Current _PATHs == saved pickle _PATHs
			self.loaded = False #Is load() called once ? 
		
	# function to add an edge to graph 
	def _addEdge(self,u,v): 
		self.graph[u].append(v) 

	'''A recursive Depth First Search function to print all paths from 'u' to 'd'. 
	visited[] keeps track of vertices in current path. 
	path[] stores actual vertices and path_index is current 
	index in path[]'''
	def _calc_paths_dfs(self, u, d, visited, path, paths): 
		# print(visited)
		# Mark the current node as visited and store in path 
		visited[u]= True
		path.append(u) 

		# If current vertex is same as destination, then print 
		# current path[] 
		if u ==d: 
			paths.append(copy.deepcopy(path))
		else: 
			# If current vertex is not destination 
			#Recur for all the vertices adjacent to this vertex 
			for i in self.graph[u]: 
				if not visited[i]: 
					self._calc_paths_dfs(i, d, visited, path, paths) 
		path.pop() 		
		visited[u]= False
		# Remove current vertex from path[] and mark it as unvisited 
	# Returns all paths from 's' to 'd' sorted by path length
	def _calc_paths_list(self,s, d): 

		# Mark all the vertices as not visited 
		visited =[False]*(self.V) 

		# Create an array to store paths 
		path = [] 

		# Create empty list of paths from s to d
		paths = []
		
		# Call the recursive helper function to print all paths 
		self._calc_paths_dfs(s, d,visited, path, paths)

		paths.sort(key=len) #Sort list of lists by length of sublists

		# path_lengths = [len(p) for p in paths]
		return paths

	def _param_to_str(self, acep, aps):
		return str(acep) + '-' + str(aps)

	def getPaths(self, acep, aps, src, dst):
			
		pstr = self._param_to_str(acep, aps)
		if not pstr in self._PATHs.keys():
			self._PATHs[pstr] = [ [ None for i in range(self.V) ] for i in range(self.V) ]
			self.sync = False
		if not self._PATHs[pstr][src][dst]:
			# Path search dfs function:
			paths = self._calc_paths_list(src, dst)
			ijpaths = ijPaths(paths)
			self._PATHs[DefaultParams][src][dst] = ijpaths
			# Proning function:
			p_ijpaths = ijpaths.prone(acep, aps)
			self._PATHs[pstr][src][dst] = p_ijpaths
			self.sync = False

		self._PATHs[pstr][src][dst].print_stats(acep, aps)
		return self._PATHs[pstr][src][dst]
	
	def printPaths (self, acep, aps, src, dst):
		pstr = self._param_to_str(acep, aps)
		if not pstr in self._PATHs.keys():
			print("There is not any path for acep = {}, aps = {}. Run:\n".format(acep, aps))
			print("g.getPaths({}, {}, {}, {})".format( acep, aps, src, dst ))
		elif not self._PATHs[pstr][src][dst]:
			print("The path is not found in _PATHS[\"{}\"]. Run:\n".format(pstr))
			print("g.getPaths({}, {}, {}, {})".format( acep, aps, src, dst))
		else:
			paths = self._PATHs[pstr][src][dst]
			paths.Print()

	def save(self, dir_to_save = None, filename = None, pstr = None):
		directory = dir_to_save or dataset_pkl_dir(self.dataset)
		fname = filename or self.topology + "_PATHs"
		dict_to_save = {}
		if pstr:
			fname = fname + "({})".format(pstr)
			dict_to_save[pstr] = self._PATHs[pstr]
		else: 
			dict_to_save = self._PATHs
		save_as_pkl(dict_to_save, os.path.join(directory, fname))
		if not pstr:
			self.sync = True
		
	def load(self, dir_to_save = None, filename = None, merge = True, pstr = None):
		directory = dir_to_save or dataset_pkl_dir(self.dataset)
		fname = filename or self.topology + "_PATHs.pkl"
		filename = os.path.join(directory, fname)

		if pstr:
			fname = fname + "({})".format(pstr)
		loaded_PATHs = load_pkl_json(filename)
		if loaded_PATHs:
			if merge:
				self._PATHs.update(loaded_PATHs)
				print("{} merged with loaded pkl.".format(fname))
			else:
				self._PATHs = loaded_PATHs
				print("{}} changed to loaded pkl.".format(fname))
		if not pstr:
			self.loaded = True

	def PATHs(self, acep, aps, src = -1, dst = -1):
		pstr = self._param_to_str(acep, aps)
		if not pstr in self._PATHs.keys():
			return None
		else:
			if src != -1 and dst != -1:
				print(' ---- src {} dst {}'.format(src, dst))
				return self._PATHs[pstr][src][dst]
			elif src == dst == -1:
				return self._PATHs[pstr]
			elif dst == -1:
				return self._PATHs[pstr][src]
			else:
				return None

	'''
	save_at:  If it is 10, after each 10 New paths calculation, the <topology>_PATHs will be saved
	sources: list of sources, None = all 
	dests: list of destinations, None = all
	'''
	def save_paths_from_to(self, acep, aps, save_at = 50, sources = None, dests = None, dont_load = False):
		srcs = sources or range(self.V)
		dsts = dests or range(self.V)
		pstr = self._param_to_str(acep, aps)
		if not self.loaded and not dont_load:
			self.load(pstr=pstr)
			self.load(pstr=DefaultParams)
		i = 0
		start_time = time.time()
		print(' //// srcs {} dsts {} V={}'.format(sources, dsts, self.V))

		for src in srcs:
			for dst in dsts:
				if self.PATHs(acep, aps, src, dst):
					print("EXIST: PATHs({}, {}, {}, {})".format(acep, aps, src, dst))
				else:
					x = self.getPaths(acep, aps, src, dst)
					i = i+1
					print("CREATED {}: PATHs({}, {}, {}, {})".format(i, acep, aps, src, dst))
					if i == save_at:
						print("\nSaving ...")
						self.save(pstr=pstr)
						i = 0
		print("\nEND. Saving ...")
		self.save()
		print("+++ (%s seconds) (N= %d acep= %.2f aps= %.2f) " % (round((time.time() - start_time),2), self.V, acep, aps ))

	def get_paths_from_to(self, acep, aps, sources = None, dests = None, dont_load = False):
		pstr = self._param_to_str(acep, aps)
		self.save_paths_from_to(acep, aps, sources=sources, dests = None, dont_load = dont_load)
		srcs = sources or range(self.V)
		pathList = [self.PATHs(acep, aps, src = source) for source in srcs]
		import gc
		gc.collect()
		return pathList

def example():
	examplestr = '''
g = Graph(TOPOLOGY)
acep = 0.9
aps = 4.0 
pathlist = g.get_paths_from_to(acep, aps, sources = [1])
pathlist_stats(pathlist, verbosity = 2)
DIR = os.path.join(dataset_pkl_dir(), g.topology+"_pathlist.json")
pathlist_export(pathlist, DIR, e = False, as_json = True)
	'''
	print(examplestr)
def help():
	helpstr = '''
# Graph(TOPOLOGY)

# load(self, dir_to_save = None, filename = None, merge = True, pstr = None)
# save(self, dir_to_save = None, filename = None, pstr = None)

# save_paths_from_to(self, acep, aps, save_at = 50, sources = None, dests = None, dont_load = False)
# get_paths_from_to(self, acep, aps, sources = None, dests = None, dont_load = False)

x = g.getPaths(acep, aps, src, dst)
x.Print()
g.save()
FullPaths = g._PATHs[DefaultParams][src][dst]
g.save_paths_from_to(acep, aps, 30)

misc:
g.getPaths(acep, aps, 1, 2)
g.printPaths(acep, aps, 1, 2)
g._PATHs.keys()
g._PATHs['0.8-3.0'][1][2].Print()
g.save_paths_from_to(acep, aps)
# pathlist_export(pathlist, output_pkl, e = False, as_json = False)


'''
	print(helpstr)

print("help()\nexample()\nexit() or Ctrl+D")
