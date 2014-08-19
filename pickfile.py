import cPickle as pickle
import gzip

def save(object, filename, bin = 1):
	file = gzip.GzipFile(filename, 'wb')
	file.write(pickle.dumps(object, bin))
	file.close()

def load(object,filename):
	file = gzip.GzipFile(filename, 'rb')
	object = pickle.loads(file.read())
	file.close()
	return object