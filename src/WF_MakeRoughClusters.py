#!/usr/bin/env python

import sys, os, BlastHandling, pickle, logging, shutil
import networkx as nx

def usage():
	print """Creates rough clusters based on the BLAST output.  
	
	WF_MakeRoughClusters.py [node dir] [node name] [min best hit] [child1] [child2]
	
	where [node dir] contains data pertinent to [node name], which has children [child1] and [child2]. 
	Tightness of intra-rough-cluster relationships can be regulated by [min best hit].
	
	[node dir], dir path
	full path to directory
	[node name], string
	name of node that [node dir] refers to
	[child1|2] string
	immediate children of [node name]
	[min best hit] float
	range is (0.0,1.0], 0.0+ is least stringent, 1.0 is most stringent
	"""
	sys.exit(1)
	
def main(argv):
	node_dir = argv[0]
	node = argv[1]
	min_best_hit = float(argv[2])
	homScale = float(argv[3])
	synScale = float(argv[4])
	numHits = int(argv[5])
	minSynFrac = float(argv[6])
	children = argv[7:]
	my_dir = node_dir+node+"/"
	blast_out = my_dir+"blast.m8"
	n_head = my_dir+"blast_headers.txt"

	FORMAT = "%(asctime)-15s %(levelname)s %(module)s.%(name)s.%(funcName)s at %(lineno)d :\n\t%(message)s\n"
	logger = logging.getLogger()
	logging.basicConfig(filename = my_dir + 'MakeRoughClusters.log', format = FORMAT, filemode='w', level=logging.DEBUG)
	# add a new Handler to print all INFO and above messages to stdout
	ch = logging.StreamHandler(sys.stdout)
	ch.setLevel(logging.INFO)
	logger.addHandler(ch)
	logger.info('Started')
	
	if "TREES_FINISHED" in os.listdir(my_dir):
		sys.exit(0)
	#get synteny data
	pickleSyn = {}
	for c in children:
		synFile = node_dir+c+"/synteny_data.pkl"
		pklFile = open(synFile, 'rb')
		pickleSyn[c] = pickle.load(pklFile)
		pklFile.close()

	#Create rough clusters with trees
	bp = BlastHandling.BlastParse(blast_out)
	hits = bp.readBlastM8()
	#~ hits = bp.readBlat()
		
	(bestHits,bestDirHits) = bp.scoreHits(hits,n_head,min_best_hit,pickleSyn,numHits,minSynFrac)
	tree_dir = my_dir+"trees"
	#if "trees" in os.listdir(my_dir):
	if os.path.exists(tree_dir):
		if not "old" in os.listdir(my_dir):
			os.mkdir(os.path.join(my_dir, "old"))
			#os.system("mkdir "+my_dir+"old")
		#os.system("mv -f "+tree_dir+"/ "+my_dir+"old/")
		shutil.move(tree_dir, os.path.join(my_dir, "old"))
	#os.system("mkdir "+tree_dir)
	os.mkdir(tree_dir)
	tree_dir = tree_dir + os.sep
	retval = bp.makePutativeClusters(bestHits,tree_dir,pickleSyn, homScale, synScale,bestDirHits, numHits)
	if retval > 0:
		sys.exit(retval)
	
	trees_done_file = my_dir+"TREES_FINISHED"
	tf = open(trees_done_file,'w')
	tf.write("Way to go!\n")
	tf.close()
	
	sys.exit(0)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
	else:
		main(sys.argv[1:])